"""
Abstract base classes for the recovery module.

Owner: Member 2.
Contract owner: Member 3 (do not change without a PR approved by both members).
"""

from __future__ import annotations

import abc

from app.schemas.recovery import RecoveryEvent, ReplicaHealth


class HealthChecker(abc.ABC):
    """
    Polls each configured application replica for health status.

    Implementations:
      - ``HttpHealthChecker`` (health_checker.py): HTTP GET to each replica URL.
    """

    @abc.abstractmethod
    def check_all(self) -> list[ReplicaHealth]:
        """
        Poll every URL in ``Settings.REPLICA_URLS`` and return a health
        snapshot for each replica.

        Returns:
            One ``ReplicaHealth`` per configured replica, with the ``healthy``
            flag and latency populated.
        """


class RecoveryManager(abc.ABC):
    """
    Takes recovery actions for unhealthy replicas.

    Implementations:
      - ``DefaultRecoveryManager`` (recovery_manager.py).
    """

    @abc.abstractmethod
    def recover(self, unhealthy: list[ReplicaHealth]) -> list[RecoveryEvent]:
        """
        Attempt to recover each unhealthy replica.

        Args:
            unhealthy: Replicas reported unhealthy by ``HealthChecker.check_all()``.

        Returns:
            One ``RecoveryEvent`` per recovery attempt.
        """

    @abc.abstractmethod
    def restore_routing(self, replica_id: str) -> RecoveryEvent:
        """
        Add a previously-removed replica back to the Nginx upstream pool.

        Args:
            replica_id: Identifier of the replica to restore.

        Returns:
            A ``RecoveryEvent`` describing the result.
        """
