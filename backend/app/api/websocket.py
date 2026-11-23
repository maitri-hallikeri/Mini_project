"""
WebSocket endpoint for the live dashboard feed.

Owner: Member 3 (backend core).

Endpoint: ws://<host>/ws/live

On connect the server sends a ``hello`` message, then stays open and forwards
every event published to the in-memory ``event_bus``.

Message envelope (all messages, in both directions)::

    {
        "type": "<str>",
        "timestamp": "<ISO-8601 UTC>",
        "payload": { ... }
    }

Allowed server→client types:
  hello          — sent immediately on connect.
  risk_update    — payload: RiskAssessment (see schemas/detection.py).
  mitigation_event — payload: MitigationAction (see schemas/mitigation.py).
  health_update  — payload: list[ReplicaHealth] (see schemas/recovery.py).
  incident_update — payload: Incident (see schemas/incident.py).

Client→server messages are accepted but ignored in this scaffold.
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import UTC, datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.orchestrator.event_bus import event_bus

logger = logging.getLogger(__name__)

ws_router = APIRouter()

ALLOWED_TYPES = frozenset(
    {"hello", "risk_update", "mitigation_event", "health_update", "incident_update"}
)


def _now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.now(UTC).isoformat()


def _envelope(event_type: str, payload: object) -> str:
    """Serialise a message envelope to a JSON string."""
    return json.dumps(
        {"type": event_type, "timestamp": _now_iso(), "payload": payload},
        default=str,
    )


@ws_router.websocket("/ws/live")
async def websocket_live(websocket: WebSocket) -> None:
    """
    Live dashboard WebSocket endpoint.

    Protocol:
      1. Accept the connection.
      2. Send a ``hello`` frame immediately.
      3. Subscribe to the event bus.
      4. Forward each published event to this client until disconnect.
      5. Unsubscribe on disconnect (clean up the queue).
    """
    await websocket.accept()
    logger.info("WebSocket client connected: %s", websocket.client)

    # Send the hello handshake
    await websocket.send_text(_envelope("hello", {}))

    # Subscribe — get a per-client asyncio.Queue
    queue: asyncio.Queue = event_bus.subscribe()

    try:
        while True:
            # Wait for the next event from the bus with a short timeout so we
            # can also detect a disconnected client promptly.
            try:
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
            except TimeoutError:
                # No events in 30 s — send a ping-style keepalive.
                await websocket.send_text(_envelope("hello", {}))
                continue

            event_type: str = event.get("type", "unknown")
            payload: object = event.get("payload", {})

            if event_type in ALLOWED_TYPES:
                await websocket.send_text(_envelope(event_type, payload))

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected: %s", websocket.client)
    finally:
        event_bus.unsubscribe(queue)
