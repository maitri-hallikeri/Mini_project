"""
Traffic feature extractor — stub implementation.

Owner: Member 1.
# TODO(member1): implement WindowFeatureExtractor
"""

from __future__ import annotations

from datetime import datetime

from app.modules.traffic_analysis.interfaces import FeatureExtractor
from app.schemas.traffic import RequestLogRecord, WindowFeatures


class WindowFeatureExtractor(FeatureExtractor):
    """
    Computes all ``WindowFeatures`` fields from a list of ``RequestLogRecord``
    objects within a single time window.

    TODO(member1):
      - ``total_requests``, ``requests_per_sec``: simple count / duration.
      - ``unique_ips``, ``top_ip``, ``top_ip_share``, ``max_requests_per_ip``,
        ``mean_requests_per_ip``: Counter over ``remote_addr``.
      - ``top_endpoint``, ``top_endpoint_share``: Counter over ``path``.
      - ``status_4xx_rate``, ``status_5xx_rate``: count 400-499 / 500-599.
      - ``avg_latency_ms``, ``p95_latency_ms``: numpy percentile over
        ``request_time_ms``.
      - ``burstiness``: coefficient of variation of per-second counts.
        (std / mean of the per-second histogram).
    """

    def extract(
        self,
        records: list[RequestLogRecord],
        window_start: datetime,
        window_end: datetime,
    ) -> WindowFeatures:
        """
        Raises:
            NotImplementedError: TODO(member1): compute all WindowFeatures fields.
        """
        raise NotImplementedError(
            "TODO(member1): compute all WindowFeatures fields from records"
        )
