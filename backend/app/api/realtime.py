from __future__ import annotations

import asyncio
from collections.abc import AsyncIterable

from fastapi import APIRouter, Request
from fastapi.sse import EventSourceResponse, ServerSentEvent

from backend.app.services.realtime_service import (
    realtime_status,
    subscribe,
    unsubscribe,
)


router = APIRouter(
    prefix="/api/v1/realtime",
    tags=["Realtime"],
)


@router.get("/health")
async def realtime_health():
    return {
        "system": "ATUL realtime change stream",
        **realtime_status(),
    }


@router.get("/stream", response_class=EventSourceResponse)
async def realtime_stream(request: Request) -> AsyncIterable[ServerSentEvent]:
    queue = await subscribe()

    try:
        yield ServerSentEvent(
            event="connected",
            data={
                "system": "ATUL",
                "message": "Real-time stream connected",
                "channel": "atul_realtime",
            },
            retry=5000,
        )

        while True:
            if await request.is_disconnected():
                break

            try:
                payload = await asyncio.wait_for(
                    queue.get(),
                    timeout=15,
                )

                event_name = str(
                    payload.get(
                        "event",
                        payload.get(
                            "type",
                            "database_change",
                        ),
                    )
                )

                yield ServerSentEvent(
                    event=event_name,
                    data=payload,
                    retry=5000,
                )

            except asyncio.TimeoutError:
                yield ServerSentEvent(
                    comment="ATUL realtime heartbeat",
                )

    finally:
        unsubscribe(queue)
