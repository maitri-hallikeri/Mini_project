"""
Temporal persistence detector.

Tracks consecutive windows with request rates above the
normal-traffic P95 threshold.

This is an additional detector. It does not modify or replace
the existing P99Detector.
"""

import csv
from dataclasses import dataclass
from pathlib import Path

from app.schemas.traffic import WindowFeatures


@dataclass
class PersistenceResult:
    triggered: bool
    consecutive_windows: int
    observed_requests_per_sec: float
    threshold: float
    description: str


class TemporalPersistenceDetector:
    """Detect sustained elevated request rates across windows."""

    def __init__(
        self,
        required_windows: int = 3,
        baseline_path: str | Path | None = None,
    ) -> None:

        if required_windows <= 0:
            raise ValueError("required_windows must be positive")

        self.required_windows = required_windows
        self.consecutive_windows = 0

        if baseline_path is None:
            baseline_path = (
                Path(__file__).resolve().parents[3]
                / "data"
                / "normal_baseline.csv"
            )

        self.threshold = self._load_p95_threshold(baseline_path)

    @staticmethod
    def _load_p95_threshold(baseline_path: str | Path) -> float:
        path = Path(baseline_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Baseline file not found: {path}"
            )

        with path.open("r", newline="") as file:
            reader = csv.reader(file)

            header = next(reader, None)

            if not header or "p95" not in header:
                raise ValueError(
                    "P95 column missing from baseline file"
                )

            p95_index = header.index("p95")

            for row in reader:
                if not row:
                    continue

                # The first column contains the feature name.
                feature_name = row[0].strip()

                if feature_name == "requests_per_second":
                    return float(row[p95_index])

        raise ValueError(
            "requests_per_second P95 threshold missing "
            "from baseline file"
        )

    def evaluate(
        self,
        features: WindowFeatures,
    ) -> PersistenceResult:

        observed_rate = features.requests_per_sec

        if observed_rate > self.threshold:
            self.consecutive_windows += 1
        else:
            self.consecutive_windows = 0

        triggered = (
            self.consecutive_windows >= self.required_windows
        )

        if triggered:
            description = (
                f"Request rate exceeded normal P95 threshold "
                f"for {self.consecutive_windows} consecutive "
                f"windows."
            )
        else:
            description = (
                f"Persistence not established. "
                f"{self.consecutive_windows}/"
                f"{self.required_windows} consecutive "
                f"windows above P95."
            )

        return PersistenceResult(
            triggered=triggered,
            consecutive_windows=self.consecutive_windows,
            observed_requests_per_sec=observed_rate,
            threshold=self.threshold,
            description=description,
        )

    def reset(self) -> None:
        """Reset the consecutive-window counter."""
        self.consecutive_windows = 0
