"""
Mitigation actions router.

Owner: Member 3 (backend core).  Rollback logic: Member 2 + Member 3.

GET  /api/v1/mitigations              — empty list until pipeline is wired.
POST /api/v1/mitigations/{id}/rollback — 501 stub.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.schemas.mitigation import ActionStatus, MitigationAction

router = APIRouter()


@router.get(
    "",
    response_model=list[MitigationAction],
    summary="List mitigation actions",
    description=(
        "Returns applied mitigation actions.  "
        "Filter by status (ACTIVE, EXPIRED, ROLLED_BACK, FAILED).  "
        "Returns an empty list until the pipeline is running."
    ),
)
def list_mitigations(
    status: ActionStatus | None = Query(default=None, description="Filter by action status."),
    db: Session = Depends(get_db_session),
) -> list[MitigationAction]:
    """
    Return mitigation actions, optionally filtered by status.

    TODO(member3): call MitigationRepository(db).list(status) once implemented.
    """
    return []


@router.post(
    "/{action_id}/rollback",
    summary="Roll back a mitigation action",
    description=(
        "Manually rolls back (cancels) an ACTIVE mitigation action before it expires.  "
        "Not yet implemented — returns 501."
    ),
    status_code=501,
)
def rollback_mitigation(
    action_id: str = Path(..., description="UUID of the mitigation action to roll back."),
    db: Session = Depends(get_db_session),
) -> dict:
    """
    Roll back a mitigation action.

    TODO(member2/member3): implement rollback logic in MitigationController,
    update action status to ROLLED_BACK via MitigationRepository, and write an
    AuditRecord via AuditRepository.
    """
    return {"detail": "TODO(member2/member3): not implemented", "code": "NOT_IMPLEMENTED"}
