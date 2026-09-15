import logging
from datetime import datetime, timezone, timedelta
from typing import List
from fastapi import APIRouter, HTTPException
from ..models import PortOrder, PortStatus
from .. import storage
from ..database import PortOrderRow, get_session

logger = logging.getLogger("uvicorn.error")

router = APIRouter(prefix="/orders", tags=["orders"])

STEP_DELAY = 10


def _to_model(row: PortOrderRow) -> PortOrder:
    return PortOrder(
        e164=row.e164,
        customer_id=row.customer_id,
        status=row.status,
        next_action_at=row.next_action_at,
        version=row.version,
    )


@router.post("/{e164}/reserve", response_model=PortOrder)
async def reserve(e164: str):
    with get_session() as session:
        row = session.query(PortOrderRow).filter_by(e164=e164).first()

        if not row:
            raise HTTPException(status_code=404, detail=f"No port order found for {e164}")

        allowed = [PortStatus.AVAILABLE, PortStatus.REJECTED]
        if PortStatus(row.status) not in allowed:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot reserve from status {row.status}",
            )

        row.status = PortStatus.RESERVED.value
        row.next_action_at = datetime.now(timezone.utc) + timedelta(seconds=STEP_DELAY)
        row.version += 1
        session.commit()
        session.refresh(row)

        storage.outbox.append({"topic": "port-order-status", "payload": {"event_type": "RESERVED", "e164": e164}})
        logger.info(f"📌 {e164}: → RESERVED (poller armed)")
        return _to_model(row)


@router.post("/{e164}/release", response_model=PortOrder)
async def release(e164: str):
    with get_session() as session:
        row = session.query(PortOrderRow).filter_by(e164=e164).first()

        if not row:
            raise HTTPException(status_code=404, detail=f"No port order found for {e164}")

        if PortStatus(row.status) != PortStatus.ACTIVE:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot release from status {row.status}",
            )

        row.status = PortStatus.RELEASED.value
        row.next_action_at = None
        row.version += 1
        session.commit()
        session.refresh(row)

        storage.outbox.append({"topic": "port-order-status", "payload": {"event_type": "RELEASED", "e164": e164}})
        logger.info(f"🔓 {e164}: ACTIVE → RELEASED")
        return _to_model(row)


@router.get("/", response_model=List[PortOrder])
def list_orders():
    with get_session() as session:
        rows = session.query(PortOrderRow).all()
        return [_to_model(r) for r in rows]


@router.get("/{e164}", response_model=PortOrder)
def get_order(e164: str):
    with get_session() as session:
        row = session.query(PortOrderRow).filter_by(e164=e164).first()
        if not row:
            raise HTTPException(status_code=404, detail=f"No port order found for {e164}")
        return _to_model(row)
