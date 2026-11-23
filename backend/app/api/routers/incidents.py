"""
Incidents router.

Owner: Member 3 (backend core).

GET /api/v1/incidents       — empty list until pipeline is wired.
GET /api/v1/incidents/{id}  — 404 JSON error when nothing stored yet.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.core.errors import not_found
from app.schemas.incident import Incident

router = APIRouter()


@router.get(
    "",
    response_model=list[Incident],
    summary="List incidents",
    description=(
        "Returns all recorded DDoS incidents, newest first. "
        "Empty until the pipeline is running."
    ),
)
def list_incidents(
    db: Session = Depends(get_db_session),
) -> list[Incident]:
    """
    Return all incidents.

    TODO(member3): call IncidentRepository(db).list() once implemented.
    """
    return []


@router.get(
    "/{incident_id}",
    response_model=Incident,
    summary="Get incident by ID",
    description=(
        "Returns the full incident record including all mitigation actions "
        "and timing milestones."
    ),
    responses={
        404: {
            "description": "Incident not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Incident 'abc123' not found.", "code": "NOT_FOUND"}
                }
            },
        }
    },
)
def get_incident(
    incident_id: str,
    db: Session = Depends(get_db_session),
) -> Incident:
    """
    Return a single incident by ID.

    Returns 404 with a standard JSON error body when no incident with the
    given ID exists (which is always the case until the pipeline runs).

    TODO(member3): call IncidentRepository(db).get(incident_id) and assemble
    the full Pydantic schema including actions once implemented.
    """
    raise not_found("Incident", incident_id)
