"""
P99-based DDoS detector.

Owner: Member 1 (traffic analysis and detection).

Uses the original normal-traffic P99 thresholds and weighted indicators.
This module is independent of the existing Member 2 detection modules.

The thresholds were calibrated using 10-second traffic windows.
"""

from __future__ import annotations

import csv
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from app.schemas.detection import (
    RiskAssessment,
    RiskLevel,
    Scenario,
    SignalEvidence,
)
from app.schemas.traffic import RequestLogRecord, WindowFeatures

Classification = Literal["BENIGN", "SUSPICIOUS", "ATTACK"]


@dataclass(frozen=True)
class P99DetectionResult:
    """Result from the P99 detector, including additional detection details."""

    classification: Classification
    risk_assessment: RiskAssessment
    candidate_source_ips: list[dict[str, str | int | float]]
    suspicious_endpoints: list[str]


class P99Detector:
    """
    Detects abnormal traffic using the original normal-traffic P99 baseline.

    Original score thresholds:
        0-24:  BENIGN
        25-49: SUSPICIOUS
        50-100: ATTACK
    """

    WINDOW_DURATION_SECONDS = 10.0

    ERROR_STATUS_CODES = {400, 403, 404, 500, 503}

    # Original detector weights. Their sum is 100.
    SIGNAL_WEIGHTS = {
        "unique_source_ips": 10,
        "max_requests_per_ip": 10,
        "max_endpoint_concentration": 15,
        "avg_latency_ms": 15,
        "p95_latency_ms": 15,
        "error_rate": 15,
        "rate_limit_rate": 10,
        "requests_per_second": 10,
    }

    DEFAULT_BASELINE_PATH = (
        Path(__file__).resolve().parents[3]
        / "data"
        / "normal_baseline.csv"
    )

    def __init__(
        self,
        baseline_path: Path | str | None = None,
    ) -> None:

        self.baseline_path = (
            Path(baseline_path)
            if baseline_path is not None
            else self.DEFAULT_BASELINE_PATH
        )

        self.thresholds = self._load_thresholds()

    def _load_thresholds(self) -> dict[str, float]:
        """
        Load P99 thresholds from the original baseline CSV.

        Uses Python's standard csv module, so pandas is not required.
        """

        if not self.baseline_path.exists():
            raise FileNotFoundError(
                f"P99 baseline file not found: {self.baseline_path}"
            )

        thresholds = {}

        with self.baseline_path.open(
            "r",
            newline="",
            encoding="utf-8",
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:
                feature_name = (
                    row.get("feature")
                    or row.get("")
                )

                p99_value = row.get("p99")

                if feature_name and p99_value:
                    thresholds[feature_name.strip()] = float(p99_value)

        missing_features = (
            set(self.SIGNAL_WEIGHTS) - set(thresholds)
        )

        if missing_features:
            raise ValueError(
                "Missing P99 thresholds for: "
                + ", ".join(sorted(missing_features))
            )

        return thresholds

    def _extract_extra_features(
        self,
        records: Sequence[RequestLogRecord],
    ) -> tuple[float, float, Counter]:
        """
        Calculate features that are not fully available in WindowFeatures.

        Returns:
            error_rate
            rate_limit_rate
            source IP request counts
        """

        total_requests = len(records)

        if total_requests == 0:
            return 0.0, 0.0, Counter()

        error_count = sum(
            1
            for record in records
            if record.status in self.ERROR_STATUS_CODES
        )

        rate_limit_count = sum(
            1
            for record in records
            if record.status == 429
        )

        source_ip_counts = Counter(
            record.remote_addr for record in records
        )

        error_rate = error_count / total_requests

        rate_limit_rate = rate_limit_count / total_requests

        return (
            error_rate,
            rate_limit_rate,
            source_ip_counts,
        )

    def assess(
        self,
        features: WindowFeatures,
        records: Sequence[RequestLogRecord],
    ) -> P99DetectionResult:
        """
        Assess one completed traffic window.

        Args:
            features: Aggregated features for the window.
            records: Original request records belonging to that window.

        Returns:
            P99DetectionResult containing the classification,
            RiskAssessment, candidate IPs and suspicious endpoints.
        """

        if abs(
            features.duration_s - self.WINDOW_DURATION_SECONDS
        ) > 1e-9:
            raise ValueError(
                "P99 thresholds are calibrated for 10-second windows. "
                f"Received {features.duration_s}-second window."
            )

        if len(records) != features.total_requests:
            raise ValueError(
                "The number of request records does not match "
                "features.total_requests."
            )

        (
            error_rate,
            rate_limit_rate,
            source_ip_counts,
        ) = self._extract_extra_features(records)

        # Map the original eight P99 indicators to the new shared schema.
        observed_values = {
            "unique_source_ips": features.unique_ips,
            "max_requests_per_ip": features.max_requests_per_ip,
            "max_endpoint_concentration": features.top_endpoint_share,
            "avg_latency_ms": features.avg_latency_ms,
            "p95_latency_ms": features.p95_latency_ms,
            "error_rate": error_rate,
            "rate_limit_rate": rate_limit_rate,
            "requests_per_second": features.requests_per_sec,
        }

        risk_score = 0.0
        signals = []

        triggered_features = set()

        for feature_name, original_weight in self.SIGNAL_WEIGHTS.items():

            observed_value = float(observed_values[feature_name])
            threshold = self.thresholds[feature_name]

            triggered = observed_value > threshold

            weight = original_weight / 100.0

            if triggered:
                risk_score += original_weight
                triggered_features.add(feature_name)

            description = (
                f"{feature_name}: observed {observed_value:.4f}, "
                f"P99 threshold {threshold:.4f}. "
                + (
                    "Threshold exceeded."
                    if triggered
                    else "Within the P99 threshold."
                )
            )

            signals.append(
                SignalEvidence(
                    name=feature_name,
                    observed_value=observed_value,
                    baseline_value=None,
                    threshold=threshold,
                    deviation=None,
                    weight=weight,
                    triggered=triggered,
                    description=description,
                )
            )

        risk_score = round(risk_score, 2)

        # Preserve the original classification thresholds.
        if risk_score >= 50:
            classification: Classification = "ATTACK"
            risk_level = RiskLevel.HIGH

        elif risk_score >= 25:
            classification = "SUSPICIOUS"
            risk_level = RiskLevel.MEDIUM

        else:
            classification = "BENIGN"
            risk_level = RiskLevel.LOW

        # Identify suspicious source IPs using the original threshold.
        ip_threshold = self.thresholds["max_requests_per_ip"]

        candidate_source_ips = []

        for source_ip, request_count in source_ip_counts.items():

            if request_count > ip_threshold:
                candidate_source_ips.append(
                    {
                        "source_ip": source_ip,
                        "request_count": request_count,
                        "requests_per_second": round(
                            request_count / features.duration_s,
                            4,
                        ),
                    }
                )

        candidate_source_ips.sort(
            key=lambda item: item["request_count"],
            reverse=True,
        )

        # Identify the endpoint responsible for unusually
        # concentrated traffic.
        suspicious_endpoints = []

        if (
            "max_endpoint_concentration" in triggered_features
            and features.top_endpoint is not None
        ):
            suspicious_endpoints.append(features.top_endpoint)

        # BENIGN traffic must never be assigned an attack scenario.
        if classification == "BENIGN":
            scenario = Scenario.NONE

        elif "max_endpoint_concentration" in triggered_features:
            scenario = Scenario.ENDPOINT_FLOOD

        elif triggered_features.intersection(
            {
                "unique_source_ips",
                "max_requests_per_ip",
                "requests_per_second",
            }
        ):
            scenario = Scenario.REQUEST_FLOOD

        else:
            scenario = Scenario.UNKNOWN

        risk_assessment = RiskAssessment(
            window_start=features.window_start,
            window_end=features.window_end,
            score=risk_score,
            level=risk_level,
            scenario=scenario,
            signals=signals,
            offending_ips=[
                item["source_ip"]
                for item in candidate_source_ips
            ],
            offending_endpoints=suspicious_endpoints,
            detectors_used=["P99Detector"],
        )

        return P99DetectionResult(
            classification=classification,
            risk_assessment=risk_assessment,
            candidate_source_ips=candidate_source_ips,
            suspicious_endpoints=suspicious_endpoints,
        )
