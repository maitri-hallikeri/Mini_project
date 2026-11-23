"""
Detection and risk-scoring schemas.

Owner: Member 2 owns the logic that produces these values.
       Member 3 owns the model definitions.
Any field change requires a pull request approved by both owners.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, Field

from app.schemas.common import UTCDatetime


class RiskLevel(StrEnum):
    """Ordered risk levels produced by the detection engine."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Scenario(StrEnum):
    """
    Attack scenario labels assigned by the detection engine.

    NONE        — no attack detected, normal traffic.
    REQUEST_FLOOD    — large overall request volume from distributed sources.
    ENDPOINT_FLOOD   — single endpoint hammered at high rate.
    BURST_ANOMALY    — sudden short spike that deviates from baseline.
    UNKNOWN          — anomaly detected but pattern does not fit known types.
    """

    NONE = "NONE"
    REQUEST_FLOOD = "REQUEST_FLOOD"
    ENDPOINT_FLOOD = "ENDPOINT_FLOOD"
    BURST_ANOMALY = "BURST_ANOMALY"
    UNKNOWN = "UNKNOWN"


class SignalEvidence(BaseModel):
    """
    Evidence from one detector signal that contributed to the risk score.

    Produced by each ``Detector.evaluate()`` call and collected into the
    final ``RiskAssessment.signals`` list.
    """

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "top_ip_share",
                    "observed_value": 0.72,
                    "baseline_value": 0.15,
                    "threshold": 0.5,
                    "deviation": 11.4,
                    "weight": 0.3,
                    "triggered": True,
                    "description": "Top IP holds 72% of requests (baseline 15%, threshold 50%).",
                }
            ]
        }
    }

    name: str = Field(..., description="Signal / feature name (matches a WindowFeatures field).")
    observed_value: float = Field(..., description="The value measured in the current window.")
    baseline_value: float | None = Field(
        default=None, description="Baseline mean for this hour bucket, if available."
    )
    threshold: float | None = Field(
        default=None, description="Hard threshold that triggers this signal, if applicable."
    )
    deviation: float | None = Field(
        default=None,
        description="Z-score: (observed - baseline_mean) / baseline_std. Null if no baseline yet.",
    )
    weight: float = Field(
        ..., ge=0.0, le=1.0, description="Contribution weight used by the risk scorer."
    )
    triggered: bool = Field(
        ...,
        description="True if this signal fired (threshold crossed or z-score high).",
    )
    description: str = Field(
        ..., description="Human-readable explanation of why this signal triggered."
    )


class RiskAssessment(BaseModel):
    """
    Full risk assessment for one traffic window.

    Produced by ``detection.engine.DetectionEngine.assess()``.
    Stored in the database via ``repositories.risk``.
    Served by ``GET /api/v1/risk/current`` and ``GET /api/v1/risk/history``.
    """

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "window_start": "2026-11-23T10:00:00Z",
                    "window_end": "2026-11-23T10:00:10Z",
                    "score": 78.5,
                    "level": "HIGH",
                    "scenario": "ENDPOINT_FLOOD",
                    "signals": [
                        {
                            "name": "top_ip_share",
                            "observed_value": 0.72,
                            "baseline_value": 0.15,
                            "threshold": 0.5,
                            "deviation": 11.4,
                            "weight": 0.3,
                            "triggered": True,
                            "description": "Top IP holds 72% of requests.",
                        }
                    ],
                    "offending_ips": ["198.51.100.43"],
                    "offending_endpoints": ["/login"],
                    "detectors_used": ["RuleDetector", "StatisticalDetector"],
                }
            ]
        }
    }

    window_start: UTCDatetime
    window_end: UTCDatetime
    score: Annotated[float, Field(ge=0.0, le=100.0)] = Field(
        ..., description="Composite risk score from 0 (clean) to 100 (critical attack)."
    )
    level: RiskLevel
    scenario: Scenario = Scenario.NONE
    signals: list[SignalEvidence] = Field(default_factory=list)
    offending_ips: list[str] = Field(
        default_factory=list, description="IPs flagged as suspicious in this window."
    )
    offending_endpoints: list[str] = Field(
        default_factory=list, description="Endpoints flagged as targeted in this window."
    )
    detectors_used: list[str] = Field(
        default_factory=list, description="Names of detectors that ran (e.g. RuleDetector)."
    )
