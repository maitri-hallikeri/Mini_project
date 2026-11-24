"""
Unit tests for the Detection module (Owner: Member 2).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.modules.detection.engine import DetectionEngine
from app.modules.detection.risk_scoring import WeightedRiskScorer
from app.modules.detection.rules import RuleDetector
from app.modules.detection.statistical import StatisticalDetector
from app.schemas.detection import RiskLevel, Scenario
from app.schemas.traffic import BaselineProfile, PerHourStats, WindowFeatures


def _make_window(
    rps: float = 15.0,
    top_ip_share: float = 0.15,
    top_endpoint_share: float = 0.25,
    status_5xx_rate: float = 0.0,
    avg_latency_ms: float = 12.0,
) -> WindowFeatures:
    start = datetime(2026, 11, 24, 10, 0, 0, tzinfo=UTC)
    return WindowFeatures(
        window_start=start,
        window_end=start + timedelta(seconds=10),
        duration_s=10.0,
        total_requests=int(rps * 10),
        requests_per_sec=rps,
        unique_ips=10,
        top_ip="198.51.100.43",
        top_ip_share=top_ip_share,
        max_requests_per_ip=int(rps * 10 * top_ip_share),
        mean_requests_per_ip=rps,
        top_endpoint="/login",
        top_endpoint_share=top_endpoint_share,
        status_4xx_rate=0.01,
        status_5xx_rate=status_5xx_rate,
        avg_latency_ms=avg_latency_ms,
        p95_latency_ms=avg_latency_ms * 1.5,
        burstiness=1.1,
    )


def _make_baseline() -> BaselineProfile:
    return BaselineProfile(
        sample_count=120,
        last_updated=datetime(2026, 11, 24, 9, 50, 0, tzinfo=UTC),
        requests_per_sec={"10": PerHourStats(mean=15.0, std=3.0)},
        unique_ips={"10": PerHourStats(mean=10.0, std=2.0)},
        top_ip_share={"10": PerHourStats(mean=0.15, std=0.04)},
        top_endpoint_share={"10": PerHourStats(mean=0.25, std=0.05)},
        status_5xx_rate={"10": PerHourStats(mean=0.001, std=0.002)},
        avg_latency_ms={"10": PerHourStats(mean=12.0, std=2.5)},
    )


def test_normal_traffic_scores_low():
    engine = DetectionEngine(
        detectors=[RuleDetector(), StatisticalDetector()],
        scorer=WeightedRiskScorer(),
    )
    assessment = engine.assess(_make_window(), _make_baseline())
    assert assessment.level == RiskLevel.LOW
    assert assessment.scenario == Scenario.NONE
    assert assessment.score == 0.0
    assert assessment.detectors_used == ["RuleDetector", "StatisticalDetector"]


def test_ddos_flood_escalates_to_critical_with_multiple_signals():
    engine = DetectionEngine(
        detectors=[RuleDetector(), StatisticalDetector()],
        scorer=WeightedRiskScorer(),
    )
    attack_window = _make_window(
        rps=250.0,
        top_ip_share=0.85,
        top_endpoint_share=0.90,
        status_5xx_rate=0.25,
        avg_latency_ms=120.0,
    )
    assessment = engine.assess(attack_window, _make_baseline())
    assert assessment.level == RiskLevel.CRITICAL
    assert assessment.score >= 85.0
    assert assessment.scenario == Scenario.ENDPOINT_FLOOD
    assert "198.51.100.43" in assessment.offending_ips
    assert "/login" in assessment.offending_endpoints


def test_single_signal_guard_prevents_false_high_or_critical():
    # Even if thresholds are tuned low so 1 signal gives 70 points,
    # 1 triggered signal must be capped at MEDIUM (< 2 signals).
    scorer = WeightedRiskScorer(medium_min=10, high_min=20, critical_min=30)
    rule_detector = RuleDetector(max_rps=50.0)  # Only RPS triggers (weight 0.30 / 1.00 = 30.0)
    engine = DetectionEngine(detectors=[rule_detector], scorer=scorer)

    assessment = engine.assess(_make_window(rps=80.0), baseline=None)
    assert assessment.level == RiskLevel.MEDIUM