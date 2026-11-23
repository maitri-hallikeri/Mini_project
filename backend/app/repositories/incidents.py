"""
Repository for incident records.

Owner: Member 3 (backend core).
TODO(member3): implement add, get, list, update with real query logic.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.models.incident import Incident
from app.schemas.incident import IncidentStatus

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class IncidentRepository:
    """
    CRUD access to the ``incidents`` table.

    Args:
        db: An open SQLAlchemy ``Session``.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, incident: Incident) -> Incident:
        """
        Persist a new ``Incident`` ORM row.

        Args:
            incident: Fully-constructed ``Incident`` ORM object (not Pydantic schema).

        Returns:
            The same row after the session flush (id populated).

        Raises:
            NotImplementedError: Until Member 3 implements this method.
        """
        raise NotImplementedError("TODO(member3): insert Incident row into incidents table")

    def get(self, incident_id: str) -> Incident | None:
        """
        Retrieve a single incident by UUID string primary key.

        Returns:
            The ``Incident`` ORM row or ``None`` if not found.

        Raises:
            NotImplementedError: Until Member 3 implements this method.
        """
        raise NotImplementedError("TODO(member3): query incidents by id")

    def list(
        self,
        status: IncidentStatus | None = None,
        limit: int = 100,
    ) -> list[Incident]:
        """
        Return incidents, optionally filtered by status.

        Args:
            status: If given, return only incidents with this status.
            limit: Maximum number of rows to return.

        Raises:
            NotImplementedError: Until Member 3 implements this method.
        """
        raise NotImplementedError("TODO(member3): list incidents with optional status filter")

    def update(self, incident: Incident) -> Incident:
        """
        Persist changes to an existing ``Incident`` ORM row.

        Args:
            incident: The row (already fetched) with updated fields.

        Returns:
            The updated row after flush.

        Raises:
            NotImplementedError: Until Member 3 implements this method.
        """
        raise NotImplementedError("TODO(member3): flush updated Incident row")
