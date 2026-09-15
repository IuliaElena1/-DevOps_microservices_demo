import asyncio
import json
import os
import logging
from aiokafka import AIOKafkaConsumer
from .database import PhoneNumberRow, get_session

logger = logging.getLogger("uvicorn.error")

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")


async def consume_registration_status():
    """
    Ascultă registration-status și scrie semnătura în DB
    când Registration Service confirmă/refuză atestarea.
    """
    consumer = AIOKafkaConsumer(
        "registration-service",
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="number-inventory-service",
    )
    await consumer.start()
    logger.info("📡 Consumer registration-status pornit.")

    try:
        async for msg in consumer:
            event = json.loads(msg.value.decode("utf-8"))
            event_type = event.get("event_type")
            e164 = event.get("e164")
            signature = event.get("signature")

            logger.info(f"📨 [registration-status] {event_type} pentru {e164}")

            with get_session() as session:
                row = session.query(PhoneNumberRow).filter_by(e164=e164).first()
                if not row:
                    logger.warning(f"⚠️ Numărul {e164} nu există în DB, skip.")
                    continue

                if event_type == "REGISTERED":
                    row.signature = signature
                    session.commit()
                    logger.info(f"✅ Semnătură salvată pentru {e164}: {signature[:8]}...")

                elif event_type == "REGISTRATION_FAILED":
                    logger.warning(f"❌ Atestare refuzată pentru {e164} (signature rămâne null)")

                elif event_type == "DEREGISTERED":
                    logger.info(f"🗑️ Deregistrat {e164} la provider.")

    finally:
        await consumer.stop()


async def consume_port_order_status():
    """
    Ascultă port-order-status și actualizează statusul numărului
    pe baza evenimentelor de portare de la Port Order Service.
    """
    consumer = AIOKafkaConsumer(
        "port-order-status",
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="inventory-port-order",
    )
    await consumer.start()
    logger.info("📡 Consumer port-order-status pornit.")

    STATUS_MAP = {
        "RESERVED": "RESERVED",
        "ACTIVE":   "ACTIVE",
        "REJECTED": "AVAILABLE",
        "RELEASED": "RELEASED",
    }

    try:
        async for msg in consumer:
            event = json.loads(msg.value.decode("utf-8"))
            event_type = event.get("event_type")
            e164 = event.get("e164")

            logger.info(f"📨 [port-order-status] {event_type} pentru {e164}")

            new_status = STATUS_MAP.get(event_type)
            if not new_status:
                logger.warning(f"⚠️ Event necunoscut: {event_type}, skip.")
                continue

            with get_session() as session:
                row = session.query(PhoneNumberRow).filter_by(e164=e164).first()
                if not row:
                    logger.warning(f"⚠️ Numărul {e164} nu există în DB, skip.")
                    continue

                old_status = row.status
                row.status = new_status
                row.version += 1
                session.commit()
                logger.info(f"✅ Status actualizat: {old_status} → {row.status} (v{row.version})")

    finally:
        await consumer.stop()
