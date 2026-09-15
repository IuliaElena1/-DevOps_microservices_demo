import json
import os
import logging
from aiokafka import AIOKafkaConsumer
from .database import PortOrderRow, get_session

logger = logging.getLogger("uvicorn.error")

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")


async def consume_number_inventory():
    """
    Ascultă number-inventory-service și creează un port_order
    pentru fiecare număr nou (NUMBER_CREATED).
    """
    consumer = AIOKafkaConsumer(
        "number-inventory-service",
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id="port-order-service",
    )
    await consumer.start()
    logger.info("📡 Consumer number-inventory-service pornit.")

    try:
        async for msg in consumer:
            event = json.loads(msg.value.decode("utf-8"))
            event_type = event.get("event")
            e164 = event.get("e164")

            if event_type == "NUMBER_CREATED":
                with get_session() as session:
                    existing = session.query(PortOrderRow).filter_by(e164=e164).first()
                    if not existing:
                        session.add(PortOrderRow(e164=e164))
                        session.commit()
                        logger.info(f"📋 Port order creat pentru {e164}")
    finally:
        await consumer.stop()
