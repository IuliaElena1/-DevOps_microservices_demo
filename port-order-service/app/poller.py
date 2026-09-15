import asyncio
import logging
from datetime import datetime, timezone, timedelta
from . import storage
from .database import PortOrderRow, get_session
from .models import PortStatus

logger = logging.getLogger("uvicorn.error")

POLL_INTERVAL = 5
STEP_DELAY    = 10


async def poll():
    logger.info("🔄 Poller started.")
    while True:
        await asyncio.sleep(POLL_INTERVAL)
        now = datetime.now(timezone.utc)
        with get_session() as session:
            orders = (
                session.query(PortOrderRow)
                .filter(
                    PortOrderRow.next_action_at != None,
                    PortOrderRow.next_action_at <= now,
                )
                .all()
            )
            for row in orders:
                _advance(row, now)
            session.commit()


def _advance(row: PortOrderRow, now: datetime):
    if row.status == PortStatus.RESERVED:
        row.status = PortStatus.SUBMITTED_AND_PENDING.value
        row.next_action_at = now + timedelta(seconds=STEP_DELAY)
        row.version += 1
        storage.outbox.append({"topic": "port-order-status", "payload": {"event_type": "SUBMITTED_AND_PENDING", "e164": row.e164}})
        logger.info(f"📬 {row.e164}: RESERVED → SUBMITTED_AND_PENDING")

    elif row.status == PortStatus.SUBMITTED_AND_PENDING:
        if row.e164.endswith("9"):
            row.status = PortStatus.REJECTED.value
            row.next_action_at = None
            row.version += 1
            storage.outbox.append({"topic": "port-order-status", "payload": {"event_type": "REJECTED", "e164": row.e164}})
            logger.info(f"❌ {row.e164}: SUBMITTED_AND_PENDING → REJECTED (ends in 9)")
        else:
            row.status = PortStatus.APPROVED.value
            row.next_action_at = now + timedelta(seconds=STEP_DELAY)
            row.version += 1
            logger.info(f"✅ {row.e164}: SUBMITTED_AND_PENDING → APPROVED")

    elif row.status == PortStatus.APPROVED:
        row.status = PortStatus.ACTIVE.value
        row.next_action_at = None
        row.version += 1
        storage.outbox.append({"topic": "port-order-status", "payload": {"event_type": "ACTIVE", "e164": row.e164}})
        logger.info(f"🟢 {row.e164}: APPROVED → ACTIVE")
