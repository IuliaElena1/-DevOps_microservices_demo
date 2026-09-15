import asyncio
import logging
from . import storage, kafka_producer

logger = logging.getLogger("uvicorn.error")


async def relay():
    logger.info("📮 Outbox relay started.")
    while True:
        while storage.outbox:
            event = storage.outbox[0]  # peek — nu scoate până nu e confirmat
            try:
                await kafka_producer.publish(event["topic"], event["payload"])
                storage.outbox.pop(0)
                logger.info(f"📤 Outbox → Kafka: {event['payload'].get('event_type')} for {event['payload'].get('e164')}")
            except Exception as e:
                logger.warning(f"⚠️ Outbox relay failed, will retry: {e}")
                await asyncio.sleep(1)
                break
        await asyncio.sleep(0.5)
