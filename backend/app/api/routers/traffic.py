"""
Traffic window router.

Owner: Member 3 (backend core).

GET /api/v1/traffic/windows — returns an empty list until the pipeline is wired.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.schemas.traffic import WindowFeatures

router = APIRouter()


@router.get(
    "/windows",
    response_model=list[WindowFeatures],
    summary="List recent traffic windows",
    description=(
        "Returns aggregated feature snapshots for recent time windows.  "
        "Returns an empty list until the pipeline is running."
    ),
)
def list_windows(
    limit: int = Query(
        default=100, ge=1, le=1000,
        description="Maximum number of windows to return.",
    ),
    since: datetime | None = Query(
        default=None,
        description="Return only windows after this UTC timestamp.",
    ),
    db: Session = Depends(get_db_session),
) -> list[WindowFeatures]:
    """
    Return recent traffic windows.

    TODO(member3): call WindowRepository(db).list(limit, since) once implemented.
    """
    return []
