"""
HTTP health checker — stub implementation.

Owner: Member 2.
# TODO(member2): implement HttpHealthChecker
# TODO(member2): adapt from protection_engine/app/recovery.py
# RecoveryManager._is_container_healthy()
"""

from __future__ import annotations

from app.modules.recovery.interfaces import HealthChecker
from app.schemas.recovery import ReplicaHealth


class HttpHealthChecker(HealthChecker):
    """
    Polls each replica URL with an HTTP GET request and records latency.

    Args:
        replica_urls: List of base URLs from ``Settings.replica_url_list``.
        timeout_s:    Per-request timeout in seconds.

    TODO(member2): adapt from protection_engine/app/recovery.py —
    ``RecoveryManager._is_container_healthy()`` already shows the pattern.
    Replace Docker-SDK calls with plain HTTP GET requests (use ``httpx``).
    """

    def __init__(self, replica_urls: list[str], timeout_s: float = 5.0) -> None:
        self._urls = replica_urls
        self._timeout = timeout_s

    def check_all(self) -> list[ReplicaHealth]:
        """
        Raises:
            NotImplementedError: TODO(member2): HTTP GET each replica and return ReplicaHealth.
        """
        raise NotImplementedError(
            "TODO(member2): HTTP GET each replica URL, measure latency, "
            "and return list[ReplicaHealth]"
        )
