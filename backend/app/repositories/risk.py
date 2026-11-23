"""
Repository for risk assessment records.

Owner: Member 3 (backend core).
TODO(member3): implement add, get, list, latest with real query logic.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from app.models.risk_assessment import RiskAssessmentModel
from app.schemas.detection import RiskAssessment

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class RiskRepository:
    """
    CRUD access to the ``risk_assessments`` table.

    Args:
        db: An open SQLAlchemy ``Session``.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, assessment: RiskAssessment) -> RiskAssessmentModel:
        """
        Persist a new ``RiskAssessment``.

        Args:
            assessment: The assessment produced by the detection engine.

        Returns:
            The newly inserted ``RiskAssessmentModel`` ORM row.

        Raises:
            NotImplementedError: Until Member 3 implements this method.
        """
        raise NotImplementedError(
            "TODO(member3): serialise RiskAssessment and insert into risk_assessments"
        )

    def get(self, assessment_id: int) -> RiskAssessmentModel | None:
        """
        Retrieve a single assessment by primary key.

        Raises:
            NotImplementedError: Until Member 3 implements this method.
        """
        raise NotImplementedError("TODO(member3): query risk_assessments by id")

    def latest(self) -> RiskAssessmentModel | None:
        """
        Return the most recent assessment, or ``None`` if the table is empty.

        Used by ``GET /api/v1/risk/current``.

        Raises:
            NotImplementedError: Until Member 3 implements this method.
        """
        raise NotImplementedError("TODO(member3): select most recent row from risk_assessments")

    def list(
        self,
        limit: int = 100,
        since: datetime | None = None,
    ) -> list[RiskAssessmentModel]:
        """
        Return recent assessments ordered by ``window_start`` descending.

        Raises:
            NotImplementedError: Until Member 3 implements this method.
        """
        raise NotImplementedError("TODO(member3): list risk_assessments with optional since filter")
