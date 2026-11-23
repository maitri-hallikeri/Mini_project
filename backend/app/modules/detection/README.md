# detection — Module README

**Owner:** Member 2

---

## Purpose

This module receives `WindowFeatures` and an optional `BaselineProfile` from
the traffic analysis module, runs three layered detectors, and returns a
`RiskAssessment` with an explainable risk score, level, and the evidence
behind each signal.

---

## Inputs

| Source | Type |
|---|---|
| `traffic_analysis.FeatureExtractor` | `WindowFeatures` |
| `traffic_analysis.BaselineStore` | `BaselineProfile \| None` |

## Outputs

| Destination | Type |
|---|---|
| `orchestrator.Pipeline` | `RiskAssessment` |
| `repositories.risk.RiskRepository` | `RiskAssessment` (via orchestrator) |
| `modules.mitigation.MitigationController` | `RiskAssessment` (via orchestrator) |

---

## Detector stack

| Priority | Detector | Always active? | Trigger condition |
|---|---|---|---|
| 1 | `RuleDetector` | Yes | Hard threshold breached |
| 2 | `StatisticalDetector` | Yes | Z-score > threshold vs baseline |
| 3 | `MLDetector` | No (`ML_DETECTOR_ENABLED=false`) | Isolation Forest anomaly score |

---

## Default risk-to-level policy (thresholds from Settings — to be tuned by Member 2)

| Score range | Level |
|---|---|
| 0 – RISK_MEDIUM_MIN-1 (default 29) | LOW |
| RISK_MEDIUM_MIN – RISK_HIGH_MIN-1 (30 – 59) | MEDIUM |
| RISK_HIGH_MIN – RISK_CRITICAL_MIN-1 (60 – 84) | HIGH |
| ≥ RISK_CRITICAL_MIN (85+) | CRITICAL |

HIGH requires ≥ 2 triggered signals; CRITICAL requires ≥ 3.

---

## File map

| File | Class | Responsibility |
|---|---|---|
| `interfaces.py` | `Detector`, `RiskScorer`, `DetectionEngineBase` | Abstract contracts |
| `rules.py` | `RuleDetector` | Hard-limit threshold checks |
| `statistical.py` | `StatisticalDetector` | Z-score vs baseline |
| `ml_detector.py` | `MLDetector` | Optional Isolation Forest |
| `risk_scoring.py` | `WeightedRiskScorer` | Signal aggregation → score |
| `engine.py` | `DetectionEngine` | Wired orchestration (partially implemented) |

---

## TODO checklist

- [ ] `RuleDetector.evaluate()` — threshold rules (adapt from `protection_engine/app/decision_engine.py`)
- [ ] `StatisticalDetector.evaluate()` — z-score computation
- [ ] `MLDetector.evaluate()` — Isolation Forest scoring (optional)
- [ ] `WeightedRiskScorer.score()` — weighted aggregation + multi-signal guard
- [ ] Unit tests in `tests/modules/detection/`

---

## Schema contract

Schemas are in `app/schemas/detection.py` (owned by Member 3).
**Do not modify schemas without opening a PR approved by both Member 2 and Member 3.**
