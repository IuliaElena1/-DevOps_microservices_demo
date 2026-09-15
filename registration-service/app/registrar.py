from .signer import sign
from . import kafka_producer


async def register(e164: str):
    signature = sign(e164)

    if signature:
        await kafka_producer.publish("registration-service", {
            "event_type": "REGISTERED",
            "e164": e164,
            "signature": signature,
        })
    else:
        await kafka_producer.publish("registration-service", {
            "event_type": "REGISTRATION_FAILED",
            "e164": e164,
            "signature": None,
        })


async def deregister(e164: str):
    print(f"[Registration] Removed {e164} from provider.")
    await kafka_producer.publish("registration-service", {
        "event_type": "DEREGISTERED",
        "e164": e164,
        "signature": None,
    })
