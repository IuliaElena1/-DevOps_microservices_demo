import asyncio
import json
import os
from aiokafka import AIOKafkaProducer

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")

producer: AIOKafkaProducer | None = None


async def start_producer():
    global producer
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    for attempt in range(10):
        try:
            await producer.start()
            return
        except Exception as e:
            print(f"Kafka not ready (attempt {attempt + 1}/10): {e}")
            await asyncio.sleep(3)
    raise RuntimeError("Could not connect to Kafka after 10 attempts")


async def stop_producer():
    if producer:
        await producer.stop()


async def publish(topic: str, event: dict):
    if producer:
        await producer.send_and_wait(
            topic,
            json.dumps(event).encode("utf-8"),
        )
