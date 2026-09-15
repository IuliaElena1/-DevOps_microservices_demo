import asyncio
import json
import os
from aiokafka import AIOKafkaConsumer
from . import kafka_producer
from .registrar import register, deregister

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")


async def main():
    consumer = AIOKafkaConsumer(
        'number-inventory-service',
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id='registration-service',
    )

    await kafka_producer.start_producer()
    await consumer.start()

    try:
        # BUCLEA PRINCIPALĂ (THE CONSUMER LOOP IS THE PROGRAM)
        async for msg in consumer:
            event = json.loads(msg.value.decode('utf-8'))

            new_status = event.get('new_status')

            if new_status == 'ACTIVE':
                await register(event['e164'])
            elif new_status == 'RELEASED':
                await deregister(event['e164'])
    finally:
        await consumer.stop()
        await kafka_producer.stop_producer()


if __name__ == "__main__":
    asyncio.run(main())
