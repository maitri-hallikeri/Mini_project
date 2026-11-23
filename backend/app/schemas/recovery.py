"""
Recovery and replica health schemas.

Owner: Member 2 owns the logic that produces these values.
       Member 3 owns the model definitions.
Any field change requires a pull request approved by both owners.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from app.schemas.common import UTCDatetime


class ReplicaHealth(BaseModel):
    """
    Health snapshot of one application replica at a point in time.

    Produced by ``recovery.health_checker.HealthChecker.check_all()``.
    Served by ``GET /api/v1/replicas``.
    """

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "replica_id": "app1",
                    "url": "http://app1:8080",
                    "healthy": True,
                    "latency_ms": 8.3,
                    "consecutive_failures": 0,
                    "last_checked": "2026-11-23T10:00:05Z",
                }
            ]
        }
    }

    replica_id: str = Field(..., description="Stable identifier for the replica (e.g. 'app1').")
    url: str = Field(..., description="Base URL used for health-check requests.")
    healthy: bool = Field(..., description="True if the last check succeeded.")
    latency_ms: float | None = Field(
        default=None,
        ge=0.0,
        description="Round-trip latency of the last health probe in milliseconds.",
    )
    consecutive_failures: int = Field(
        ..., ge=0, description="Number of consecutive failed health checks."
    )
    last_checked: UTCDatetime = Field(..., description="Timestamp of the last health check.")


class RecoveryAction(StrEnum):
    """
    Types of recovery action the manager can take.

    RESTART              — restart the replica process / container.
    REMOVE_FROM_ROUTING  — remove the replica from the Nginx upstream pool.
    RESTORE_ROUTING      — add the replica back to the upstream pool after recovery.
    """

    RESTART = "RESTART"
    REMOVE_FROM_ROUTING = "REMOVE_FROM_ROUTING"
    RESTORE_ROUTING = "RESTORE_ROUTING"


class RecoveryEvent(BaseModel):
    """
    Record of one recovery action taken for a replica.

    Produced by ``recovery.recovery_manager.RecoveryManager.recover()``.
    Stored and served as part of an incident's timeline.
    """

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "replica_id": "app1",
                    "action": "RESTART",
                    "success": True,
                    "timestamp": "2026-11-23T10:00:30Z",
                    "details": {"recovery_time_s": 4.2},
                }
            ]
        }
    }

    replica_id: str = Field(..., description="ID of the replica this action targeted.")
    action: RecoveryAction
    success: bool = Field(..., description="True if the action completed successfully.")
    timestamp: UTCDatetime = Field(..., description="When the recovery action was taken.")
    details: dict = Field(
        default_factory=dict,
        description="Arbitrary data (e.g. recovery_time_s, error message).",
    )
