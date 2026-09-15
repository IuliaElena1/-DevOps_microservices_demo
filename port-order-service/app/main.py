import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import orders, outbox
from . import kafka_producer
from .kafka_consumer import consume_number_inventory
from .database import create_tables
from .poller import poll
from .outbox_relay import relay

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=== Port Order Service starting ===")

    logger.info("Creating DB tables if not exist...")
    create_tables()
    logger.info("DB tables ready.")

    logger.info("Initializing Kafka Producer...")
    await kafka_producer.start_producer()
    logger.info("Kafka Producer started successfully.")

    logger.info("Starting consumer: number_inventory...")
    task_consumer = asyncio.create_task(consume_number_inventory())
    logger.info("Consumer number_inventory is active.")

    logger.info("Starting poller...")
    task_poller = asyncio.create_task(poll())
    logger.info("Poller is active.")

    logger.info("Starting outbox relay...")
    task_relay = asyncio.create_task(relay())
    logger.info("Outbox relay is active.")

    logger.info("=== All components started. Service is ready. ===")
    yield

    logger.info("=== Shutting down Port Order Service... ===")
    task_consumer.cancel()
    task_poller.cancel()
    task_relay.cancel()
    await kafka_producer.stop_producer()
    logger.info("Kafka Producer and consumers stopped. Service shut down.")


app = FastAPI(title="Port Order Service", version="0.1.0", lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(orders.router)
app.include_router(outbox.router)


@app.get("/health")
def health():
    return {"status": "ok"}
