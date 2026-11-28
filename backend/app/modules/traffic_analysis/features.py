
from __future__ import annotations

from collections import Counter
from datetime import UTC, datetime
from statistics import mean, pstdev, quantiles

from app.modules.traffic_analysis.interfaces import FeatureExtractor
from app.schemas.traffic import RequestLogRecord, WindowFeatures


class WindowFeatureExtractor(FeatureExtractor):
    """
    Extracts traffic statistics from one fixed time window.
    """

    def extract(
        self,
        records: list[RequestLogRecord],
        window_start: datetime,
        window_end: datetime,
    ) -> WindowFeatures:

        duration = (window_end - window_start).total_seconds()

        if duration <= 0:
            raise ValueError("Window duration must be positive")

        total_requests = len(records)

        ip_counts = Counter(record.remote_addr for record in records)
        endpoint_counts = Counter(record.path for record in records)

        unique_ips = len(ip_counts)

        top_ip = ip_counts.most_common(1)[0][0] if ip_counts else None
        max_requests_per_ip = max(ip_counts.values(), default=0)

        mean_requests_per_ip = (
            total_requests / unique_ips if unique_ips else 0.0
        )

        top_ip_share = (
            max_requests_per_ip / total_requests
            if total_requests else 0.0
        )

        top_endpoint = (
            endpoint_counts.most_common(1)[0][0]
            if endpoint_counts else None
        )

        top_endpoint_share = (
            endpoint_counts[top_endpoint] / total_requests
            if total_requests and top_endpoint else 0.0
        )

        status_4xx = sum(
            1 for record in records
            if 400 <= record.status <= 499
        )

        status_5xx = sum(
            1 for record in records
            if 500 <= record.status <= 599
        )

        status_4xx_rate = (
            status_4xx / total_requests if total_requests else 0.0
        )

        status_5xx_rate = (
            status_5xx / total_requests if total_requests else 0.0
        )

        latencies = [
            record.request_time_ms for record in records
        ]

        avg_latency_ms = mean(latencies) if latencies else 0.0

        if len(latencies) >= 2:
            p95_latency_ms = quantiles(
                latencies, n=100, method="inclusive"
            )[94]
        elif latencies:
            p95_latency_ms = latencies[0]
        else:
            p95_latency_ms = 0.0

        # Count requests in each second of the window.
        per_second_counts = [0] * max(1, int(duration + 0.999999))

        for record in records:
            elapsed = (
                record.timestamp - window_start
            ).total_seconds()

            second_index = int(elapsed)

            if 0 <= second_index < len(per_second_counts):
                per_second_counts[second_index] += 1

        average_per_second = mean(per_second_counts)

        if average_per_second > 0:
            burstiness = (
                pstdev(per_second_counts) / average_per_second
            )
        else:
            burstiness = 0.0

        return WindowFeatures(
            window_start=window_start.astimezone(UTC),
            window_end=window_end.astimezone(UTC),
            duration_s=duration,
            total_requests=total_requests,
            requests_per_sec=total_requests / duration,
            unique_ips=unique_ips,
            top_ip=top_ip,
            top_ip_share=top_ip_share,
            max_requests_per_ip=max_requests_per_ip,
            mean_requests_per_ip=mean_requests_per_ip,
            top_endpoint=top_endpoint,
            top_endpoint_share=top_endpoint_share,
            status_4xx_rate=status_4xx_rate,
            status_5xx_rate=status_5xx_rate,
            avg_latency_ms=avg_latency_ms,
            p95_latency_ms=p95_latency_ms,
            burstiness=burstiness,
        )
