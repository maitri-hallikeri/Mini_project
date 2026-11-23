"""
Recovery manager — stub implementation.

Owner: Member 2.
# TODO(member2): implement DefaultRecoveryManager
# TODO(member2): adapt from protection_engine/app/recovery.py RecoveryManager
"""

from __future__ import annotations

from app.modules.recovery.interfaces import RecoveryManager
from app.schemas.recovery import RecoveryEvent, ReplicaHealth


class DefaultRecoveryManager(RecoveryManager):
    """
    Attempts to recover unhealthy replicas by restarting or rerouting them.

    Recovery policy:
      1. After ``failure_threshold`` consecutive failures → RESTART.
      2. If restart fails → REMOVE_FROM_ROUTING.
      3. Once healthy again → RESTORE_ROUTING.

    TODO(member2): adapt from protection_engine/app/recovery.py —
    ``RecoveryManager.check_and_recover_all()`` contains the threshold and
    restart logic.  Replace Docker-SDK calls with the approach agreed with
    Member 3 (e.g. a Docker SDK call, a sidecar agent call, or a signal).
    """

    def recover(self, unhealthy: list[ReplicaHealth]) -> list[RecoveryEvent]:
        """
        Raises:
            NotImplementedError: TODO(member2): implement recovery logic.
        """
        raise NotImplementedError(
            "TODO(member2): attempt restart / reroute for each unhealthy replica"
        )

    def restore_routing(self, replica_id: str) -> RecoveryEvent:
        """
        Raises:
            NotImplementedError: TODO(member2): add replica back to Nginx upstream.
        """
        raise NotImplementedError(
            "TODO(member2): add replica_id back to Nginx upstream pool and return RecoveryEvent"
        )
