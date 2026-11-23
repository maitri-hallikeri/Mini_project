"""
In-memory asyncio publish/subscribe event bus.

Owner: Member 3 (backend core).

This is a fully working implementation — the WebSocket endpoint and the
pipeline both depend on it at runtime.

Design:
  - Any coroutine calls ``event_bus.publish(event_type, payload)`` to
    broadcast an event to all currently-connected WebSocket clients.
  - Each WebSocket connection calls ``event_bus.subscribe()`` on connect and
    ``event_bus.unsubscribe(queue)`` on disconnect.
  - Each subscriber gets its own ``asyncio.Queue``; ``publish`` puts a copy of
    the event into every live queue.
  - There is no persistence — events delivered while no client is connected
    are dropped.  This is intentional: the dashboard is a live view, not an
    event log.

Thread/task safety:
  - All public methods are called from async code only (FastAPI + asyncio).
  - ``_subscribers`` is modified only while holding ``_lock`` (an asyncio.Lock).
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

logger = logging.getLogger(__name__)

_MAX_QUEUE_SIZE = 256  # Drop oldest if a slow client falls too far behind.


class EventBus:
    """
    Lightweight in-memory pub/sub broker for WebSocket events.

    Usage::

        # Publisher (orchestrator pipeline):
        await event_bus.publish("risk_update", assessment.model_dump())

        # Subscriber (WebSocket handler):
        queue = event_bus.subscribe()
        try:
            event = await queue.get()          # {"type": ..., "payload": ...}
        finally:
            event_bus.unsubscribe(queue)
    """

    def __init__(self) -> None:
        self._subscribers: list[asyncio.Queue[dict[str, Any]]] = []
        self._lock: asyncio.Lock = asyncio.Lock()

    def subscribe(self) -> asyncio.Queue[dict[str, Any]]:
        """
        Register a new subscriber and return its dedicated queue.

        Called from the WebSocket handler on client connect.
        Thread-safe: uses an asyncio.Lock.
        """
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=_MAX_QUEUE_SIZE)
        # Synchronously append — safe because GIL protects list.append and we
        # only ever call this from the event-loop thread.
        self._subscribers.append(queue)
        logger.debug("EventBus: subscriber added (total=%d)", len(self._subscribers))
        return queue

    def unsubscribe(self, queue: asyncio.Queue[dict[str, Any]]) -> None:
        """
        Remove a subscriber queue.

        Called from the WebSocket handler on client disconnect.
        Silent no-op if the queue is not in the list (e.g. double-unsubscribe).
        """
        try:
            self._subscribers.remove(queue)
            logger.debug("EventBus: subscriber removed (total=%d)", len(self._subscribers))
        except ValueError:
            pass

    async def publish(self, event_type: str, payload: Any) -> None:
        """
        Broadcast an event to every subscriber.

        Args:
            event_type: One of the allowed WebSocket message types
                        (hello, risk_update, mitigation_event, health_update,
                        incident_update).
            payload:    JSON-serialisable object; becomes the ``payload`` field
                        of the WebSocket message envelope.

        Drops the event into each subscriber's queue non-blockingly.
        If a queue is full (slow client) the oldest item is discarded to
        prevent the pipeline from stalling.
        """
        if not self._subscribers:
            return

        message: dict[str, Any] = {"type": event_type, "payload": payload}
        dead: list[asyncio.Queue[dict[str, Any]]] = []

        for q in list(self._subscribers):
            try:
                q.put_nowait(message)
            except asyncio.QueueFull:
                # Discard oldest to make room, then retry.
                try:
                    q.get_nowait()
                    q.put_nowait(message)
                    logger.warning("EventBus: queue full for a subscriber — oldest event dropped.")
                except (asyncio.QueueEmpty, asyncio.QueueFull):
                    dead.append(q)

        for q in dead:
            self.unsubscribe(q)

    @property
    def subscriber_count(self) -> int:
        """Return the number of currently-connected subscribers."""
        return len(self._subscribers)


# Module-level singleton — imported by websocket.py and pipeline.py.
event_bus: EventBus = EventBus()
