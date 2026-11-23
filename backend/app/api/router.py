"""
Master API router.

Owner: Member 3 (backend core).

All versioned REST routes are assembled here and mounted with the
``API_PREFIX`` (/api/v1) in ``app/main.py``.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.routers import (
    health,
    incidents,
    metrics,
    mitigations,
    replicas,
    risk,
    traffic,
)

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(traffic.router, prefix="/traffic", tags=["traffic"])
api_router.include_router(risk.router, prefix="/risk", tags=["risk"])
api_router.include_router(mitigations.router, prefix="/mitigations", tags=["mitigations"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["incidents"])
api_router.include_router(replicas.router, prefix="/replicas", tags=["replicas"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
