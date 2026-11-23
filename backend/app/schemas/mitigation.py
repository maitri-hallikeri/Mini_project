"""
Mitigation action and audit schemas.

Owner: Member 2 owns the logic that creates these values.
       Member 3 owns the model definitions.
Any field change requires a pull request approved by both owners.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from app.schemas.common import UTCDatetime


class ActionType(StrEnum):
    """
    Types of mitigation action the controller can apply.

    LOG_ONLY            — record the event, take no traffic action.
    INCREASE_MONITORING — shorten the window and tighten thresholds temporarily.
    RATE_LIMIT          — apply per-IP or per-endpoint rate limiting in Nginx.
    PROTECT_ENDPOINT    — add stricter rules for a targeted endpoint.
    TEMP_BLOCK_IP       — temporarily deny all traffic from a specific IP.
    ROLLBACK            — undo a previous mitigation action before it expires.
    """

    LOG_ONLY = "LOG_ONLY"
    INCREASE_MONITORING = "INCREASE_MONITORING"
    RATE_LIMIT = "RATE_LIMIT"
    PROTECT_ENDPOINT = "PROTECT_ENDPOINT"
    TEMP_BLOCK_IP = "TEMP_BLOCK_IP"
    ROLLBACK = "ROLLBACK"


class ActionStatus(StrEnum):
    """Lifecycle status of a mitigation action."""

    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    ROLLED_BACK = "ROLLED_BACK"
    FAILED = "FAILED"


class MitigationAction(BaseModel):
    """
    A single mitigation action applied by the controller.

    Created by ``mitigation.controller.MitigationController.apply()``.
    Stored via ``repositories.mitigations``.
    Served by ``GET /api/v1/mitigations`` and ``GET /api/v1/incidents/{id}``.

    ``expires_at`` is required for all action types except LOG_ONLY so that
    every traffic restriction is guaranteed to self-expire.
    """

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "action_type": "TEMP_BLOCK_IP",
                    "status": "ACTIVE",
                    "target": "198.51.100.43",
                    "parameters": {"duration_s": 300},
                    "risk_level": "HIGH",
                    "reason": "Top IP holds 72% of requests in window.",
                    "incident_id": "7c8d9e0f-1234-5678-abcd-ef0123456789",
                    "created_at": "2026-11-23T10:00:10Z",
                    "expires_at": "2026-11-23T10:05:10Z",
                }
            ]
        }
    }

    id: str = Field(..., description="UUID v4 string.")
    action_type: ActionType
    status: ActionStatus = ActionStatus.ACTIVE
    target: str | None = Field(
        default=None,
        description="IP address or endpoint path that this action targets.",
    )
    parameters: dict = Field(
        default_factory=dict,
        description="Action-specific parameters (e.g. {rate: 100, burst: 20} for RATE_LIMIT).",
    )
    risk_level: str = Field(..., description="RiskLevel that triggered this action.")
    reason: str = Field(..., description="Human-readable reason for applying this action.")
    incident_id: str | None = Field(
        default=None, description="ID of the parent incident, if one has been created."
    )
    created_at: UTCDatetime
    expires_at: UTCDatetime | None = Field(
        default=None,
        description="When this action auto-expires. Required for all types except LOG_ONLY.",
    )


class AuditRecord(BaseModel):
    """
    Immutable audit entry for any event that changes mitigation state.

    Written by ``mitigation.audit.AuditLogger.record()``.
    Stored via ``repositories.audit``.
    """

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "a1b2c3d4-0000-0000-0000-000000000001",
                    "timestamp": "2026-11-23T10:00:10Z",
                    "actor": "controller",
                    "event_type": "ACTION_APPLIED",
                    "details": {"target": "198.51.100.43", "duration_s": 300},
                    "action_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                }
            ]
        }
    }

    id: str = Field(..., description="UUID v4 string.")
    timestamp: UTCDatetime
    actor: str = Field(
        ...,
        description='Who generated this event: "controller" for automated, "operator" for manual.',
    )
    event_type: str = Field(
        ...,
        description=(
            "Short label for the event "
            "(e.g. ACTION_APPLIED, ACTION_EXPIRED, ACTION_ROLLED_BACK)."
        ),
    )
    details: dict = Field(
        default_factory=dict,
        description="Arbitrary key-value data relevant to this event.",
    )
    action_id: str | None = Field(
        default=None, description="ID of the MitigationAction this event relates to, if any."
    )
