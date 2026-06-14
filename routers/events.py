import json
from datetime import datetime, timezone
from typing import Optional

import aio_pika
from fastapi import APIRouter, Request
from pydantic import BaseModel

import models
from database import db_dependency

router = APIRouter(prefix="/p", tags=["ingest"])


class Event(BaseModel):
    event_id: str
    event_name: str
    event_type: str
    timestamp: datetime
    anonymous_id: str
    user_id: Optional[int] = None
    session_id: str
    context: Optional[dict] = None
    properties: Optional[dict] = None


class EventBatch(BaseModel):
    batch: list[Event]
    sent_at: datetime


@router.post("", status_code=202)
async def ingest_events(payload: EventBatch, request: Request, db: db_dependency):
    received_at = datetime.now(timezone.utc).replace(tzinfo=None)
    channel = request.app.state.rabbit_channel

    for evt in payload.batch:
        event_data = evt.model_dump()
        event_data["timestamp"] = event_data["timestamp"].replace(tzinfo=None)

        await channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps({**event_data, "received_at": received_at.isoformat()}, default=str).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key="events",
        )

        db.add(models.Events(**event_data, received_at=received_at))

    await db.commit()
    return {"accepted": len(payload.batch)}
