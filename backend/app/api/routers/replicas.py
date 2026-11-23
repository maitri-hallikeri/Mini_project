"""
Replicas router.

Owner: Member 3 (backend core).

GET /api/v1/replicas — empty list until the health checker is wired.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.schemas.recovery import ReplicaHealth

router = APIRouter()


@router.get(
    "",
    response_model=list[ReplicaHealth],
    summary="List replica health",
    description=(
        "Returns the most recent health snapshot for every configured replica.  "
        "Returns an empty list until the health checker module is implemented."
    ),
)
def list_replicas(
    db: Session = Depends(get_db_session),
) -> list[ReplicaHealth]:
    """
    Return current replica health snapshots.

    TODO(member3): call the health checker or query the last ReplicaEvent
    per replica once the recovery module is implemented.
    """
    return []
