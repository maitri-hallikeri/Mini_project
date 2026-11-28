"""
HTTP health checker implementation.

Owner: Member 2.
"""

from __future__ import annotations

import time
from datetime import UTC, datetime
from urllib.parse import urlparse

import httpx

from app.modules.recovery.interfaces import HealthChecker
from app.schemas.recovery import ReplicaHealth


class HttpHealthChecker(HealthChecker):
    """
    Polls each replica URL with an HTTP GET request, measures latency,
    and tracks consecutive failures per replica.
    """

    def __init__(
        self,
        replica_urls: list[str],
        timeout_s: float = 5.0,
        health_path: str = "/health",
        client: httpx.Client | None = None,
    ) -> None:
        self._urls = replica_urls
        self._timeout = timeout_s
        self._health_path = health_path
        self._client = client
        self._failures: dict[str, int] = {}

    @staticmethod
    def _extract_replica_id(url: str, index: int) -> str:
        """Derive a clean replica_id like 'app1' from 'http://app1:8080'."""
        parsed = urlparse(url)
        if parsed.hostname:
            return parsed.hostname
        return f"replica-{index + 1}"

    def check_all(self) -> list[ReplicaHealth]:
        """Poll every configured replica URL and return a ReplicaHealth snapshot."""
        results: list[ReplicaHealth] = []
        own_client = self._client is None
        client = self._client or httpx.Client(timeout=self._timeout)

        try:
            for idx, base_url in enumerate(self._urls):
                replica_id = self._extract_replica_id(base_url, idx)
                probe_url = f"{base_url.rstrip('/')}{self._health_path}"
                now = datetime.now(UTC)
                t0 = time.perf_counter()

                try:
                    response = client.get(probe_url)
                    latency_ms = round((time.perf_counter() - t0) * 1000, 2)
                    healthy = 200 <= response.status_code < 400
                except httpx.HTTPError:
                    latency_ms = None
                    healthy = False

                if healthy:
                    self._failures[replica_id] = 0
                else:
                    self._failures[replica_id] = self._failures.get(replica_id, 0) + 1

                results.append(
                    ReplicaHealth(
                        replica_id=replica_id,
                        url=base_url,
                        healthy=healthy,
                        latency_ms=latency_ms,
                        consecutive_failures=self._failures[replica_id],
                        last_checked=now,
                    )
                )
        finally:
            if own_client:
                client.close()

        return results
