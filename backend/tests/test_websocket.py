"""
WebSocket contract tests.

Owner: Member 3 (backend core).
"""

from __future__ import annotations

import json


def test_websocket_connect_receives_hello(client):
    """
    Connecting to /ws/live must yield a hello message as the first frame.
    """
    with client.websocket_connect("/ws/live") as ws:
        data = ws.receive_text()
        msg = json.loads(data)
        assert msg["type"] == "hello"


def test_websocket_hello_has_timestamp(client):
    """hello message must include a timestamp field."""
    with client.websocket_connect("/ws/live") as ws:
        msg = json.loads(ws.receive_text())
        assert "timestamp" in msg


def test_websocket_hello_has_payload(client):
    """hello message must include a payload field (may be empty dict)."""
    with client.websocket_connect("/ws/live") as ws:
        msg = json.loads(ws.receive_text())
        assert "payload" in msg


def test_websocket_hello_payload_is_dict(client):
    """hello payload must be an object (dict), not null or a string."""
    with client.websocket_connect("/ws/live") as ws:
        msg = json.loads(ws.receive_text())
        assert isinstance(msg["payload"], dict)
