"""
Metrics summary router.

Owner: Member 3 (backend core).

GET /api/v1/metrics/summary — returns all-null MetricsSummary until incidents exist.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.schemas.incident import MetricsSummary

router = APIRouter()


@router.get(
    "/summary",
    response_model=MetricsSummary,
    summary="Aggregated evaluation metrics",
    description=(
        "Returns detection and mitigation latency statistics aggregated over "
        "all resolved incidents.  All float fields are null when no resolved "
        "incidents exist yet."
    ),
)
def get_metrics_summary(
    db: Session = Depends(get_db_session),
) -> MetricsSummary:
    """
    Return aggregated metrics.

    Returns the zero/null baseline until incidents are resolved.

    TODO(member3): query IncidentRepository for resolved incidents and compute
    mean latencies, availability, and success rate.
    """
    return MetricsSummary(
        incident_count=0,
        detection_latency_s=None,
        mitigation_latency_s=None,
        recovery_time_s=None,
        availability_pct=None,
        legit_success_rate_pct=None,
    )
