"""
Incident lifecycle and metrics summary schemas.

Owner: Member 3 (backend core / orchestrator).
Any field change requires a pull request approved by all members who read this schema
(Member 2 for mitigation, Member 4 for the dashboard).
"""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, Field

from app.schemas.common import UTCDatetime
from app.schemas.mitigation import MitigationAction


class IncidentStatus(StrEnum):
    """
    Lifecycle state of a DDoS incident.

    OPEN        — attack detected, no mitigation applied yet.
    MITIGATING  — at least one mitigation action is ACTIVE.
    RECOVERING  — attack subsided, verifying service health.
    RESOLVED    — service healthy, all mitigations rolled back / expired.
    """

    OPEN = "OPEN"
    MITIGATING = "MITIGATING"
    RECOVERING = "RECOVERING"
    RESOLVED = "RESOLVED"


class Incident(BaseModel):
    """
    Full incident record from detection to resolution.

    Created by the orchestrator when risk first exceeds MEDIUM.
    Updated by the orchestrator at each pipeline cycle with timing milestones.
    Served by ``GET /api/v1/incidents`` and ``GET /api/v1/incidents/{id}``.

    Timing fields (T_detect, T_mitigate, T_recover) are null until each
    milestone is reached and are used to compute evaluation metrics.
    """

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "7c8d9e0f-1234-5678-abcd-ef0123456789",
                    "status": "RESOLVED",
                    "scenario": "ENDPOINT_FLOOD",
                    "peak_risk_level": "HIGH",
                    "started_at": "2026-11-23T10:00:00Z",
                    "t_detect": "2026-11-23T10:00:03Z",
                    "t_mitigate": "2026-11-23T10:00:05Z",
                    "t_recover": "2026-11-23T10:08:30Z",
                    "legit_success_rate": 0.994,
                    "actions": [],
                }
            ]
        }
    }

    id: str = Field(..., description="UUID v4 string.")
    status: IncidentStatus = IncidentStatus.OPEN
    scenario: str = Field(..., description="Scenario label (matches detection.Scenario enum).")
    peak_risk_level: str = Field(
        ..., description="Highest RiskLevel observed during this incident."
    )
    started_at: UTCDatetime = Field(..., description="When the incident was first opened.")
    t_detect: UTCDatetime | None = Field(
        default=None,
        description="Timestamp when the detection engine first flagged the attack.",
    )
    t_mitigate: UTCDatetime | None = Field(
        default=None,
        description="Timestamp when the first mitigation action was successfully applied.",
    )
    t_recover: UTCDatetime | None = Field(
        default=None,
        description="Timestamp when all replicas were verified healthy and mitigations expired.",
    )
    legit_success_rate: Annotated[float, Field(ge=0.0, le=1.0)] | None = Field(
        default=None,
        description=(
            "Fraction of legitimate (non-blocked) requests that received a 2xx response "
            "during the incident window. Null until the incident is resolved."
        ),
    )
    actions: list[MitigationAction] = Field(
        default_factory=list,
        description="All mitigation actions taken during this incident.",
    )


class MetricsSummary(BaseModel):
    """
    Aggregated evaluation metrics across all resolved incidents.

    Served by ``GET /api/v1/metrics/summary``.
    Used in the final project evaluation and dashboard overview card.
    All float fields are null when no resolved incidents exist yet.
    """

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "incident_count": 5,
                    "detection_latency_s": 3.2,
                    "mitigation_latency_s": 1.8,
                    "recovery_time_s": 42.5,
                    "availability_pct": 99.6,
                    "legit_success_rate_pct": 99.4,
                }
            ]
        }
    }

    incident_count: int = Field(default=0, ge=0, description="Total number of recorded incidents.")
    detection_latency_s: float | None = Field(
        default=None,
        description="Mean time from attack start to detection (T_detect - started_at) in seconds.",
    )
    mitigation_latency_s: float | None = Field(
        default=None,
        description=(
            "Mean time from detection to first mitigation "
            "(T_mitigate - T_detect) in seconds."
        ),
    )
    recovery_time_s: float | None = Field(
        default=None,
        description=(
            "Mean time from mitigation to full recovery "
            "(T_recover - T_mitigate) in seconds."
        ),
    )
    availability_pct: float | None = Field(
        default=None,
        ge=0.0,
        le=100.0,
        description="Mean service availability (%) across all incidents.",
    )
    legit_success_rate_pct: float | None = Field(
        default=None,
        ge=0.0,
        le=100.0,
        description="Mean legitimate-request success rate (%) across all incidents.",
    )
