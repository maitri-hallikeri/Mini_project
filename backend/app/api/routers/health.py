"""
Health check router.

Owner: Member 3 (backend core).

GET /api/v1/health — fully implemented; returns status, version, env,
pipeline state, and server time.  Used as the Docker healthcheck target.
"""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import get_settings_dep
from app.core.config import Settings

router = APIRouter()


class HealthResponse(BaseModel):
    """Response body for GET /health."""

    status: str
    app_version: str
    env: str
    pipeline_enabled: bool
    server_time: datetime


@router.get(
    "",
    response_model=HealthResponse,
    summary="Application health check",
    description=(
        "Returns the current health status of the backend.  "
        "Always returns HTTP 200 when the process is running.  "
        "Used by Docker Compose and load balancers."
    ),
)
def get_health(settings: Settings = Depends(get_settings_dep)) -> HealthResponse:
    """
    Return a liveness / readiness snapshot.

    This endpoint is intentionally lightweight — it performs no I/O.
    """
    return HealthResponse(
        status="ok",
        app_version=settings.APP_VERSION,
        env=settings.APP_ENV,
        pipeline_enabled=settings.PIPELINE_ENABLED,
        server_time=datetime.now(UTC),
    )
