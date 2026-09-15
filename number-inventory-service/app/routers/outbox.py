from fastapi import APIRouter, HTTPException
from .. import storage

router = APIRouter(prefix="/outbox", tags=["outbox"])


@router.get("/")
def list_outbox():
    return {"pending": len(storage.outbox), "events": storage.outbox}


@router.delete("/{index}")
def delete_outbox_event(index: int):
    if index < 0 or index >= len(storage.outbox):
        raise HTTPException(status_code=404, detail=f"No event at index {index}")
    removed = storage.outbox.pop(index)
    return {"removed": removed}


@router.post("/flush")
async def flush_outbox():
    from .. import kafka_producer
    published = []
    failed = []
    while storage.outbox:
        event = storage.outbox[0]
        try:
            await kafka_producer.publish(event["topic"], event["payload"])
            storage.outbox.pop(0)
            published.append(event)
        except Exception as e:
            failed.append({"event": event, "error": str(e)})
            break
    return {"published": len(published), "failed": len(failed), "remaining": len(storage.outbox)}
