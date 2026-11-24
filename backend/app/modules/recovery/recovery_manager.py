"""
Recovery manager implementation.

Owner: Member 2.
"""

from __future__ import annotations

import logging
import os
import time
from collections.abc import Callable
from datetime import UTC, datetime

from app.modules.recovery.interfaces import RecoveryManager
from app.schemas.recovery import RecoveryAction, RecoveryEvent, ReplicaHealth

logger = logging.getLogger(__name__)


class DefaultRecoveryManager(RecoveryManager):
    """
    Attempts to recover unhealthy replicas by restarting or rerouting them.

    Recovery policy:
      1. After ``failure_threshold`` consecutive failures -> RESTART.
      2. If restart fails -> REMOVE_FROM_ROUTING.
      3. Once healthy again -> RESTORE_ROUTING.
    """

    def __init__(
        self,
        failure_threshold: int = 3,
        restart_fn: Callable[[str], bool] | None = None,
        upstream_path: str | None = None,
    ) -> None:
        self._failure_threshold = failure_threshold
        # Optional injectable callback (e.g. Docker/sidecar restart); defaults to safe True
        self._restart_fn = restart_fn or (lambda _replica_id: True)
        self._upstream_path = upstream_path
        self._removed_from_routing: set[str] = set()
        self.events: list[RecoveryEvent] = []

    def _sync_upstream(self) -> None:
        """Write active/disabled upstream server comments if upstream_path is configured."""
        if not self._upstream_path:
            return
        parent = os.path.dirname(self._upstream_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        lines = ["# Auto-generated upstream routing state by CLOUDSHIELD\n"]
        for replica_id in sorted(self._removed_from_routing):
            lines.append(f"# server {replica_id}:8080 down;\n")
        with open(self._upstream_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

    def recover(self, unhealthy: list[ReplicaHealth]) -> list[RecoveryEvent]:
        """Attempt recovery for replicas that reached consecutive failure threshold."""
        triggered_events: list[RecoveryEvent] = []

        for replica in unhealthy:
            if replica.healthy or replica.consecutive_failures < self._failure_threshold:
                continue

            t0 = time.perf_counter()
            now = datetime.now(UTC)
            try:
                restarted = bool(self._restart_fn(replica.replica_id))
            except Exception as exc:
                logger.warning("Restart failed for %s: %s", replica.replica_id, exc)
                restarted = False

            elapsed_s = round(time.perf_counter() - t0, 3)

            if restarted:
                event = RecoveryEvent(
                    replica_id=replica.replica_id,
                    action=RecoveryAction.RESTART,
                    success=True,
                    timestamp=now,
                    details={
                        "recovery_time_s": elapsed_s,
                        "consecutive_failures": replica.consecutive_failures,
                    },
                )
                self.events.append(event)
                triggered_events.append(event)
            else:
                # Restart failed -> remove replica from Nginx upstream routing
                self._removed_from_routing.add(replica.replica_id)
                self._sync_upstream()
                event = RecoveryEvent(
                    replica_id=replica.replica_id,
                    action=RecoveryAction.REMOVE_FROM_ROUTING,
                    success=True,
                    timestamp=now,
                    details={
                        "reason": "Restart failed; removed from upstream routing.",
                        "consecutive_failures": replica.consecutive_failures,
                    },
                )
                self.events.append(event)
                triggered_events.append(event)

        return triggered_events

    def restore_routing(self, replica_id: str) -> RecoveryEvent:
        """Add a previously-removed replica back to the Nginx upstream pool."""
        self._removed_from_routing.discard(replica_id)
        self._sync_upstream()

        event = RecoveryEvent(
            replica_id=replica_id,
            action=RecoveryAction.RESTORE_ROUTING,
            success=True,
            timestamp=datetime.now(UTC),
            details={"message": f"Replica '{replica_id}' restored to routing pool."},
        )
        self.events.append(event)
        return event