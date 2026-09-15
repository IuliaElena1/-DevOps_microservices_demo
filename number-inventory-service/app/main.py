import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import numbers, outbox
from . import kafka_producer
from .kafka_consumer import consume_registration_status, consume_port_order_status
from .outbox_relay import relay
from .database import create_tables

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=== Number Inventory Service starting ===")

    logger.info("Creating DB tables if not exist...")
    create_tables()
    logger.info("DB tables ready.")

    logger.info("Initializing Kafka Producer...")
    await kafka_producer.start_producer()
    logger.info("Kafka Producer started successfully.")

    logger.info("Starting consumer: registration_status...")
    task1 = asyncio.create_task(consume_registration_status())
    logger.info("Consumer registration_status is active.")

    logger.info("Starting consumer: port_order_status...")
    task2 = asyncio.create_task(consume_port_order_status())
    logger.info("Consumer port_order_status is active.")

    logger.info("Starting outbox relay...")
    task3 = asyncio.create_task(relay())
    logger.info("Outbox relay is active.")

    logger.info("=== All components started. Service is ready. ===")
    yield

    logger.info("=== Shutting down Number Inventory Service... ===")
    task1.cancel()
    task2.cancel()
    task3.cancel()
    await kafka_producer.stop_producer()
    logger.info("Kafka Producer and consumers stopped. Service shut down.")

# Pasăm lifespan-ul către FastAPI
app = FastAPI(title="Number Inventory Service", version="0.1.0", lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(numbers.router)
app.include_router(outbox.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
