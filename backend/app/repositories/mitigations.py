"""
Repository for mitigation action records.

Owner: Member 3 (backend core).
TODO(member3): implement add, get, list, update_status with real query logic.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.models.mitigation_action import MitigationActionModel
from app.schemas.mitigation import ActionStatus, MitigationAction

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class MitigationRepository:
    """
    CRUD access to the ``mitigation_actions`` table.

    Args:
        db: An open SQLAlchemy ``Session``.
    """

    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, action: MitigationAction) -> MitigationActionModel:
        """
        Persist a new ``MitigationAction``.

        Args:
            action: The action created by the mitigation controller.

        Returns:
            The newly inserted ``MitigationActionModel`` ORM row.

        Raises:
            NotImplementedError: Until Member 3 implements this method.
        """
        raise NotImplementedError("TODO(member3): insert MitigationAction into mitigation_actions")

    def get(self, action_id: str) -> MitigationActionModel | None:
        """
        Retrieve a single action by its UUID string primary key.

        Raises:
            NotImplementedError: Until Member 3 implements this method.
        """
        raise NotImplementedError("TODO(member3): query mitigation_actions by id")

    def list(
        self,
        status: ActionStatus | None = None,
    ) -> list[MitigationActionModel]:
        """
        Return actions, optionally filtered by status.

        Args:
            status: If given, return only actions with this ``ActionStatus``.

        Raises:
            NotImplementedError: Until Member 3 implements this method.
        """
        raise NotImplementedError(
            "TODO(member3): list mitigation_actions with optional status filter"
        )

    def update_status(self, action_id: str, status: ActionStatus) -> MitigationActionModel | None:
        """
        Update the status of an existing action (e.g. EXPIRED or ROLLED_BACK).

        Raises:
            NotImplementedError: Until Member 3 implements this method.
        """
        raise NotImplementedError("TODO(member3): update status column in mitigation_actions")
