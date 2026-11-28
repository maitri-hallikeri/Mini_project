"""
Weighted risk scorer implementation.

Owner: Member 2.
"""

from __future__ import annotations

from app.core.config import get_settings
from app.modules.detection.interfaces import RiskScorer
from app.schemas.detection import RiskAssessment, RiskLevel, Scenario, SignalEvidence
from app.schemas.traffic import WindowFeatures


class WeightedRiskScorer(RiskScorer):
    """
    Combines all ``SignalEvidence`` weights into a 0-100 risk score and
    enforces multi-signal guards before escalating to HIGH or CRITICAL.
    """

    def __init__(
        self,
        medium_min: int | None = None,
        high_min: int | None = None,
        critical_min: int | None = None,
    ) -> None:
        settings = get_settings()
        self._medium_min = medium_min if medium_min is not None else settings.RISK_MEDIUM_MIN
        self._high_min = high_min if high_min is not None else settings.RISK_HIGH_MIN
        self._critical_min = (
            critical_min if critical_min is not None else settings.RISK_CRITICAL_MIN
        )

    @staticmethod
    def _classify_scenario(triggered_names: set[str], level: RiskLevel) -> Scenario:
        """Infer the attack scenario from which signals fired."""
        if level == RiskLevel.LOW or not triggered_names:
            return Scenario.NONE

        has_endpoint = any("top_endpoint_share" in n for n in triggered_names)
        has_volume = any(
            "requests_per_sec" in n or "top_ip_share" in n for n in triggered_names
        )
        has_stat_only = all(n.startswith("z_") for n in triggered_names)

        if has_endpoint:
            return Scenario.ENDPOINT_FLOOD
        if has_volume:
            return Scenario.REQUEST_FLOOD
        if has_stat_only:
            return Scenario.BURST_ANOMALY
        return Scenario.UNKNOWN

    def score(
        self,
        features: WindowFeatures,
        signals: list[SignalEvidence],
    ) -> RiskAssessment:
        """Compute weighted score, enforce multi-signal guard, and return RiskAssessment."""
        total_weight = sum(s.weight for s in signals)
        triggered = [s for s in signals if s.triggered]
        triggered_weight = sum(s.weight for s in triggered)

        if total_weight > 0:
            raw_score = (triggered_weight / total_weight) * 100.0
        else:
            raw_score = 0.0

        final_score = round(min(100.0, max(0.0, raw_score)), 2)
        triggered_count = len(triggered)

        # Map score to level using Settings thresholds
        if final_score >= self._critical_min:
            level = RiskLevel.CRITICAL
        elif final_score >= self._high_min:
            level = RiskLevel.HIGH
        elif final_score >= self._medium_min:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW

        # Multi-signal guard against single-signal false positives:
        # CRITICAL requires >= 3 triggered signals; HIGH requires >= 2.
        if level == RiskLevel.CRITICAL and triggered_count < 3:
            level = RiskLevel.HIGH if triggered_count >= 2 else RiskLevel.MEDIUM
        if level == RiskLevel.HIGH and triggered_count < 2:
            level = RiskLevel.MEDIUM

        triggered_names = {s.name for s in triggered}
        scenario = self._classify_scenario(triggered_names, level)

        offending_ips: list[str] = []
        if level != RiskLevel.LOW and features.top_ip:
            offending_ips.append(features.top_ip)

        offending_endpoints: list[str] = []
        if level != RiskLevel.LOW and features.top_endpoint:
            offending_endpoints.append(features.top_endpoint)

        return RiskAssessment(
            window_start=features.window_start,
            window_end=features.window_end,
            score=final_score,
            level=level,
            scenario=scenario,
            signals=signals,
            offending_ips=offending_ips,
            offending_endpoints=offending_endpoints,
            detectors_used=[],
        )
