from fastapi import APIRouter, HTTPException
import logging
from typing import List
from ..models import PhoneNumber, PhoneNumberCreate, PhoneStatus, StatusUpdate
from .. import storage
from ..database import PhoneNumberRow, get_session

logger = logging.getLogger("uvicorn.error")

router = APIRouter(prefix="/numbers", tags=["numbers"])

ALLOWED_TRANSITIONS = {
    PhoneStatus.AVAILABLE: [PhoneStatus.RESERVED],
    PhoneStatus.RESERVED:  [PhoneStatus.ACTIVE, PhoneStatus.AVAILABLE],
    PhoneStatus.ACTIVE:    [PhoneStatus.RELEASED],
    PhoneStatus.RELEASED:  [],
}


def _to_model(row: PhoneNumberRow) -> PhoneNumber:
    return PhoneNumber(
        id=row.id,
        e164=row.e164,
        country_code=row.country_code,
        status=row.status,
        customer_id=row.customer_id,
        current_carrier=row.current_carrier,
        signature=row.signature,
        version=row.version,
    )


@router.post("/", response_model=PhoneNumber, status_code=201)
async def create_number(payload: PhoneNumberCreate):
    logger.info(f"📥 [LOCAL APP] POST /numbers - Primit e164: {payload.e164}")

    with get_session() as session:
        if session.query(PhoneNumberRow).filter_by(e164=payload.e164).first():
            logger.warning(f"❌ [LOCAL APP] Conflict: Numărul {payload.e164} există deja.")
            raise HTTPException(status_code=409, detail=f"Number {payload.e164} already exists")

        row = PhoneNumberRow(
            e164=payload.e164,
            country_code=payload.country_code,
            current_carrier=payload.current_carrier,
        )
        session.add(row)
        session.commit()
        session.refresh(row)

        storage.outbox.append({"topic": "number-inventory-service", "payload": {
            "event":   "NUMBER_CREATED",
            "e164":    row.e164,
            "status":  row.status,
            "version": row.version,
        }})
        logger.info(f"✅ [LOCAL APP] Salvat în DB cu ID-ul {row.id}!")
        return _to_model(row)


@router.get("/", response_model=List[PhoneNumber])
def list_numbers():
    with get_session() as session:
        rows = session.query(PhoneNumberRow).all()
        logger.info(f"🔍 [LOCAL APP] GET /numbers - Total numere: {len(rows)}")
        return [_to_model(r) for r in rows]


@router.get("/{e164}", response_model=PhoneNumber)
def get_number(e164: str):
    logger.info(f"🔍 [LOCAL APP] GET /numbers/{e164}")
    with get_session() as session:
        row = session.query(PhoneNumberRow).filter_by(e164=e164).first()
        if not row:
            logger.warning(f"❌ [LOCAL APP] Numărul {e164} nu a fost găsit.")
            raise HTTPException(status_code=404, detail=f"Number {e164} not found")
        return _to_model(row)


@router.patch("/{e164}/status", response_model=PhoneNumber)
async def update_status(e164: str, payload: StatusUpdate):
    logger.info(f"📥 [LOCAL APP] PATCH /numbers/{e164}/status - Noua stare: {payload.new_status}")

    with get_session() as session:
        row = session.query(PhoneNumberRow).filter_by(e164=e164).first()
        if not row:
            logger.warning(f"❌ [LOCAL APP] Numărul {e164} nu există.")
            raise HTTPException(status_code=404, detail=f"Number {e164} not found")

        if row.version != payload.version:
            logger.warning(f"❌ [LOCAL APP] Version conflict! DB={row.version}, Req={payload.version}")
            raise HTTPException(
                status_code=409,
                detail=f"Version conflict: DB has version {row.version}, got {payload.version}",
            )

        current_status = PhoneStatus(row.status)
        if payload.new_status not in ALLOWED_TRANSITIONS[current_status]:
            logger.warning(f"❌ [LOCAL APP] Tranziție ilegală: {current_status} → {payload.new_status}")
            raise HTTPException(
                status_code=400,
                detail=f"Illegal transition: {current_status} → {payload.new_status}",
            )

        old_status = row.status
        row.status = payload.new_status.value
        row.version += 1
        session.commit()
        session.refresh(row)

        storage.outbox.append({"topic": "number-inventory-service", "payload": {
            "event":      "STATUS_CHANGED",
            "e164":       e164,
            "old_status": old_status,
            "new_status": row.status,
            "version":    row.version,
        }})
        logger.info(f"✅ [LOCAL APP] Stare actualizată: {old_status} ➔ {row.status} (v{row.version})")
        return _to_model(row)
