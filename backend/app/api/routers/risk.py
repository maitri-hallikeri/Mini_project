"""
Risk assessment router.

Owner: Member 3 (backend core).

GET /api/v1/risk/current  — returns null when no assessment exists yet.
GET /api/v1/risk/history  — returns empty list until pipeline is wired.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.schemas.detection import RiskAssessment

router = APIRouter()


@router.get(
    "/current",
    response_model=RiskAssessment | None,
    summary="Most recent risk assessment",
    description=(
        "Returns the risk assessment for the latest completed traffic window, "
        "or null if no assessment has been produced yet."
    ),
)
def get_current_risk(
    db: Session = Depends(get_db_session),
) -> RiskAssessment | None:
    """
    Return the most recent risk assessment, or null.

    TODO(member3): call RiskRepository(db).latest() once implemented.
    """
    return None


@router.get(
    "/history",
    response_model=list[RiskAssessment],
    summary="Risk assessment history",
    description="Returns all stored risk assessments ordered by window start, newest first.",
)
def list_risk_history(
    db: Session = Depends(get_db_session),
) -> list[RiskAssessment]:
    """
    Return historical risk assessments.

    TODO(member3): call RiskRepository(db).list() once implemented.
    """
    return []
