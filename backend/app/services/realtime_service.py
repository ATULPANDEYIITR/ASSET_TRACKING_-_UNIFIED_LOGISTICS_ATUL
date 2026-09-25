from __future__ import annotations

import asyncio
import json
import logging
from contextlib import suppress
from typing import Any

import psycopg

from backend.app.db.database import DATABASE_URL


logger = logging.getLogger("atul.realtime")

CHANNEL_NAME = "atul_realtime"

_subscribers: set[asyncio.Queue] = set()
_listener_task: asyncio.Task | None = None
_listener_lock: asyncio.Lock | None = None


def _get_lock() -> asyncio.Lock:
    global _listener_lock

    if _listener_lock is None:
        _listener_lock = asyncio.Lock()

    return _listener_lock


async def publish_event(payload: dict[str, Any]) -> None:
    if not _subscribers:
        return

    dead: list[asyncio.Queue] = []

    for queue in list(_subscribers):
        try:
            queue.put_nowait(payload)
        except asyncio.QueueFull:
            dead.append(queue)

    for queue in dead:
        _subscribers.discard(queue)


async def _database_listener() -> None:
    logger.info("ATUL realtime database listener starting")

    while True:
        try:
            async with await psycopg.AsyncConnection.connect(
                DATABASE_URL,
                autocommit=True,
            ) as connection:

                await connection.execute(f"LISTEN {CHANNEL_NAME}")

                logger.info(
                    "ATUL realtime listener connected to PostgreSQL channel '%s'",
                    CHANNEL_NAME,
                )

                async for notification in connection.notifies(
                    timeout=30,
                ):
                    try:
                        payload = json.loads(notification.payload)
                    except Exception:
                        payload = {
                            "type": "database_notification",
                            "channel": notification.channel,
                            "payload": notification.payload,
                        }

                    payload.setdefault("channel", notification.channel)
                    payload.setdefault("source", "postgresql")
                    payload.setdefault("pid", notification.pid)

                    await publish_event(payload)

        except asyncio.CancelledError:
            logger.info("ATUL realtime database listener stopped")
            raise

        except Exception as exc:
            logger.exception(
                "ATUL realtime database listener error: %s",
                exc,
            )

            await asyncio.sleep(3)


async def ensure_listener_started() -> None:
    global _listener_task

    async with _get_lock():
        if _listener_task is None or _listener_task.done():
            _listener_task = asyncio.create_task(
                _database_listener(),
                name="atul-postgresql-realtime-listener",
            )

            await asyncio.sleep(0)


async def subscribe() -> asyncio.Queue:
    await ensure_listener_started()

    queue: asyncio.Queue = asyncio.Queue(maxsize=1000)

    _subscribers.add(queue)

    return queue


def unsubscribe(queue: asyncio.Queue) -> None:
    _subscribers.discard(queue)


async def shutdown_listener() -> None:
    global _listener_task

    if _listener_task is not None:
        _listener_task.cancel()

        with suppress(asyncio.CancelledError):
            await _listener_task

        _listener_task = None


def realtime_status() -> dict[str, Any]:
    return {
        "online": True,
        "channel": CHANNEL_NAME,
        "listener_running": bool(
            _listener_task is not None
            and not _listener_task.done()
        ),
        "subscribers": len(_subscribers),
    }
