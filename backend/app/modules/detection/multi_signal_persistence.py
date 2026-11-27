"""
Multi-signal persistence detector.

Uses eight P95 traffic thresholds and requires at least
three indicators to exceed their thresholds for two
consecutive windows.
"""

import csv
from dataclasses import dataclass
from pathlib import Path

from app.schemas.traffic import WindowFeatures, RequestLogRecord


FEATURE_NAMES = (
    "requests_per_second",
    "unique_source_ips",
    "max_requests_per_ip",
    "max_endpoint_concentration",
    "avg_latency_ms",
    "p95_latency_ms",
    "error_rate",
    "rate_limit_rate",
)

ERROR_STATUS_CODES = {400, 403, 404, 500, 503}


@dataclass
class MultiSignalPersistenceResult:
    triggered: bool
    indicators_exceeded: int
    consecutive_windows: int
    required_windows: int
    triggered_indicators: list[str]
    observed_values: dict[str, float]
    thresholds: dict[str, float]
    description: str


class MultiSignalPersistenceDetector:

    def __init__(
        self,
        required_indicators: int = 3,
        required_windows: int = 2,
        baseline_path: str | Path | None = None,
    ) -> None:

        if not 1 <= required_indicators <= len(FEATURE_NAMES):
            raise ValueError("Invalid required_indicators")

        if required_windows <= 0:
            raise ValueError("required_windows must be positive")

        self.required_indicators = required_indicators
        self.required_windows = required_windows
        self.consecutive_windows = 0

        if baseline_path is None:
            baseline_path = (
                Path(__file__).resolve().parents[3]
                / "data"
                / "normal_baseline.csv"
            )

        self.thresholds = self._load_p95_thresholds(baseline_path)

    @staticmethod
    def _load_p95_thresholds(
        baseline_path: str | Path,
    ) -> dict[str, float]:

        path = Path(baseline_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Baseline file not found: {path}"
            )

        thresholds = {}

        with path.open("r", newline="") as file:
            reader = csv.reader(file)
            header = next(reader, None)

            if not header or "p95" not in header:
                raise ValueError("P95 column missing")

            p95_index = header.index("p95")

            for row in reader:
                if row and row[0].strip() in FEATURE_NAMES:
                    thresholds[row[0].strip()] = float(
                        row[p95_index]
                    )

        missing = set(FEATURE_NAMES) - set(thresholds)

        if missing:
            raise ValueError(
                f"Missing P95 thresholds: {sorted(missing)}"
            )

        return thresholds

    @staticmethod
    def _extract_observed_values(
        features: WindowFeatures,
        records: list[RequestLogRecord],
    ) -> dict[str, float]:

        total = len(records)

        if total == 0:
            raise ValueError("Cannot assess an empty window")

        if total != features.total_requests:
            raise ValueError(
                "Record count does not match total_requests"
            )

        error_count = sum(
            record.status in ERROR_STATUS_CODES
            for record in records
        )

        rate_limit_count = sum(
            record.status == 429
            for record in records
        )

        return {
            "requests_per_second": float(features.requests_per_sec),
            "unique_source_ips": float(features.unique_ips),
            "max_requests_per_ip": float(features.max_requests_per_ip),
            "max_endpoint_concentration": float(features.top_endpoint_share),
            "avg_latency_ms": float(features.avg_latency_ms),
            "p95_latency_ms": float(features.p95_latency_ms),
            "error_rate": error_count / total,
            "rate_limit_rate": rate_limit_count / total,
        }

    def evaluate(
        self,
        features: WindowFeatures,
        records: list[RequestLogRecord],
    ) -> MultiSignalPersistenceResult:

        observed = self._extract_observed_values(features, records)

        triggered_indicators = [
            name
            for name in FEATURE_NAMES
            if observed[name] > self.thresholds[name]
        ]

        indicators_exceeded = len(triggered_indicators)

        if indicators_exceeded >= self.required_indicators:
            self.consecutive_windows += 1
        else:
            self.consecutive_windows = 0

        triggered = (
            self.consecutive_windows >= self.required_windows
        )

        if triggered:
            description = (
                f"{indicators_exceeded} indicators exceeded P95 "
                f"for {self.consecutive_windows} consecutive windows."
            )
        else:
            description = (
                f"Persistence not established: "
                f"{indicators_exceeded} indicators exceeded P95; "
                f"{self.consecutive_windows}/"
                f"{self.required_windows} consecutive windows."
            )

        return MultiSignalPersistenceResult(
            triggered=triggered,
            indicators_exceeded=indicators_exceeded,
            consecutive_windows=self.consecutive_windows,
            required_windows=self.required_windows,
            triggered_indicators=triggered_indicators,
            observed_values=observed,
            thresholds=self.thresholds.copy(),
            description=description,
        )

    def reset(self) -> None:
        self.consecutive_windows = 0
