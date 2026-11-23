"""
Traffic analysis schemas — shared contract between Member 1 (traffic_analysis)
and Member 3 (backend core / orchestrator).

Owner: Member 1 owns the data that populates these models.
       Member 3 owns the model definitions.
Any field change requires a pull request approved by both owners.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field

from app.schemas.common import UTCDatetime


class RequestLogRecord(BaseModel):
    """
    One parsed line from the Nginx access log.

    Produced by ``traffic_analysis.parser.LogParser.parse_line()``.
    """

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "timestamp": "2026-11-23T10:00:00Z",
                    "remote_addr": "198.51.100.43",
                    "method": "GET",
                    "path": "/api/products",
                    "status": 200,
                    "bytes_sent": 1024,
                    "request_time_ms": 12.5,
                    "upstream": "http://app1:8080",
                    "user_agent": "Mozilla/5.0",
                }
            ]
        }
    }

    timestamp: UTCDatetime = Field(..., description="When the request was served.")
    remote_addr: str = Field(..., description="Client IP address.")
    method: str = Field(..., description="HTTP method (GET, POST, …).")
    path: str = Field(..., description="Request path (without query string).")
    status: int = Field(..., ge=100, le=599, description="HTTP response status code.")
    bytes_sent: int = Field(..., ge=0, description="Response body size in bytes.")
    request_time_ms: float = Field(
        ..., ge=0.0, description="Total request duration in milliseconds."
    )
    upstream: str | None = Field(default=None, description="Upstream replica URL, if proxied.")
    user_agent: str | None = Field(default=None, description="User-Agent header value.")


class WindowFeatures(BaseModel):
    """
    Aggregate traffic features for one time window.

    Produced by ``traffic_analysis.features.FeatureExtractor.extract()``.
    Consumed by ``detection.engine.DetectionEngine.assess()``.
    """

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "window_start": "2026-11-23T10:00:00Z",
                    "window_end": "2026-11-23T10:00:10Z",
                    "duration_s": 10.0,
                    "total_requests": 350,
                    "requests_per_sec": 35.0,
                    "unique_ips": 12,
                    "top_ip": "198.51.100.43",
                    "top_ip_share": 0.71,
                    "max_requests_per_ip": 250,
                    "mean_requests_per_ip": 29.2,
                    "top_endpoint": "/login",
                    "top_endpoint_share": 0.80,
                    "status_4xx_rate": 0.02,
                    "status_5xx_rate": 0.00,
                    "avg_latency_ms": 18.4,
                    "p95_latency_ms": 45.0,
                    "burstiness": 1.3,
                }
            ]
        }
    }

    window_start: UTCDatetime = Field(..., description="Inclusive start of the window.")
    window_end: UTCDatetime = Field(..., description="Exclusive end of the window.")
    duration_s: float = Field(..., gt=0.0, description="Window duration in seconds.")

    # Volume features
    total_requests: int = Field(..., ge=0)
    requests_per_sec: float = Field(..., ge=0.0)

    # IP distribution
    unique_ips: int = Field(..., ge=0)
    top_ip: str | None = Field(
        default=None,
        description="IP with the most requests (or None if no data).",
    )
    top_ip_share: Annotated[float, Field(ge=0.0, le=1.0)] = Field(
        ..., description="Fraction of total requests from top_ip."
    )
    max_requests_per_ip: int = Field(..., ge=0)
    mean_requests_per_ip: float = Field(..., ge=0.0)

    # Endpoint distribution
    top_endpoint: str | None = Field(
        default=None,
        description="Most-requested path (or None if no data).",
    )
    top_endpoint_share: Annotated[float, Field(ge=0.0, le=1.0)] = Field(
        ..., description="Fraction of total requests to top_endpoint."
    )

    # Error rates
    status_4xx_rate: Annotated[float, Field(ge=0.0, le=1.0)] = Field(
        ..., description="Proportion of responses with 4xx status."
    )
    status_5xx_rate: Annotated[float, Field(ge=0.0, le=1.0)] = Field(
        ..., description="Proportion of responses with 5xx status."
    )

    # Latency
    avg_latency_ms: float = Field(..., ge=0.0, description="Mean request latency in ms.")
    p95_latency_ms: float = Field(..., ge=0.0, description="95th-percentile request latency in ms.")

    # Burst pattern
    burstiness: float = Field(
        ...,
        description=(
            "Coefficient of variation of per-second request counts within the window. "
            "High values indicate bursty traffic."
        ),
    )


class PerHourStats(BaseModel):
    """
    Mean and standard deviation of a single feature for one hour-of-day bucket.
    Used inside ``BaselineProfile``.
    """

    mean: float = Field(..., description="Rolling mean of the feature.")
    std: float = Field(..., ge=0.0, description="Rolling standard deviation of the feature.")


class BaselineProfile(BaseModel):
    """
    Learned baseline statistics for normal traffic, bucketed by hour of day.

    Produced and updated by ``traffic_analysis.baseline.BaselineStore.update()``.
    Consumed by ``detection.engine.DetectionEngine.assess()``.
    """

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "sample_count": 1440,
                    "last_updated": "2026-11-23T09:50:00Z",
                    "requests_per_sec": {"10": {"mean": 25.0, "std": 5.0}},
                    "unique_ips": {"10": {"mean": 8.0, "std": 2.0}},
                    "top_ip_share": {"10": {"mean": 0.15, "std": 0.05}},
                    "top_endpoint_share": {"10": {"mean": 0.30, "std": 0.08}},
                    "status_5xx_rate": {"10": {"mean": 0.001, "std": 0.001}},
                    "avg_latency_ms": {"10": {"mean": 12.0, "std": 3.0}},
                }
            ]
        }
    }

    sample_count: int = Field(
        ..., ge=0,
        description="Total number of windows used to build this profile.",
    )
    last_updated: UTCDatetime = Field(..., description="Timestamp of the last update.")

    # Per-feature, per-hour-of-day statistics.
    # Keys are hour-of-day strings ("0" … "23").
    requests_per_sec: dict[str, PerHourStats] = Field(default_factory=dict)
    unique_ips: dict[str, PerHourStats] = Field(default_factory=dict)
    top_ip_share: dict[str, PerHourStats] = Field(default_factory=dict)
    top_endpoint_share: dict[str, PerHourStats] = Field(default_factory=dict)
    status_5xx_rate: dict[str, PerHourStats] = Field(default_factory=dict)
    avg_latency_ms: dict[str, PerHourStats] = Field(default_factory=dict)
