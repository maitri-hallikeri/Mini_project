# Architecture

## System overview

CLOUDSHIELD is a cloud-hosted DDoS protection system.  The backend (this
repository) is the **security controller** — it reads traffic data, detects
attacks, applies mitigations, and recovers unhealthy replicas.

The protected service is two application replicas sitting behind an Nginx
reverse proxy.  The backend talks to Nginx (to enforce blocks) and to the
replicas (to check health).

---

## End-to-end pipeline flow

```
Nginx access log
       │
       ▼
┌─────────────────────────┐
│  traffic_analysis        │  Member 1
│  NginxLogSource          │  tail access log
│  NginxLogParser          │  parse lines → RequestLogRecord
│  FixedWindowAggregator   │  bucket by time window
│  WindowFeatureExtractor  │  compute 15 features → WindowFeatures
│  InMemoryBaselineStore   │  update rolling statistics
└──────────┬──────────────┘
           │  WindowFeatures + BaselineProfile
           ▼
┌─────────────────────────┐
│  detection               │  Member 2
│  RuleDetector            │  hard-limit checks
│  StatisticalDetector     │  z-score vs baseline
│  MLDetector (optional)   │  Isolation Forest
│  WeightedRiskScorer      │  score 0-100 + level
└──────────┬──────────────┘
           │  RiskAssessment
           ▼
┌─────────────────────────┐
│  mitigation              │  Member 2
│  DefaultMitigationCtrl   │  LOW→log, MED→ratelimit,
│  NginxRuleWriter         │  HIGH→protect, CRIT→block
│  DbAuditLogger           │  write audit records
└──────────┬──────────────┘
           │  list[MitigationAction]
           ▼
┌─────────────────────────┐
│  recovery                │  Member 2
│  HttpHealthChecker       │  poll replica URLs
│  DefaultRecoveryManager  │  restart / reroute
└──────────┬──────────────┘
           │  list[RecoveryEvent]
           ▼
┌─────────────────────────┐
│  orchestrator.Pipeline   │  Member 3
│  update Incident timings │  T_detect, T_mitigate, T_recover
│  persist via repos       │
│  publish to EventBus     │
└──────────┬──────────────┘
           │  events
     ┌─────┴─────┐
     ▼           ▼
REST API     WebSocket /ws/live
(Member 3)   (Member 3)
     │           │
     └─────┬─────┘
           ▼
  React Dashboard (Member 4)
```

---

## Module dependency graph

```
schemas/  ◄── consumed by all modules and repos
   │
   ├── traffic_analysis  →  detection  →  mitigation
   │                                   →  recovery
   │
   └── orchestrator.Pipeline
           │
           ├── repositories (persist data)
           └── event_bus (broadcast to WebSocket)
```

The schemas package is the only cross-cutting dependency.  Every other
module communicates exclusively through the schema types.

---

## Data stores

| Store | Technology | Scope |
|---|---|---|
| Persistent data | SQLite (dev) / PostgreSQL (prod) | traffic windows, risk assessments, mitigations, incidents, audit log |
| Baseline statistics | In-process memory | rolling per-hour-bucket mean/std |
| Event queue | In-process asyncio.Queue per WebSocket client | live dashboard feed |

---

## Configuration hot-spots

All settings live in `app/core/config.py` (source of truth) and are
documented with example values in `.env.example`.

Risk thresholds (`RISK_MEDIUM_MIN`, `RISK_HIGH_MIN`, `RISK_CRITICAL_MIN`)
are placeholder values — **Member 2 must tune them** using benchmark results.

---

## Offline benchmark pipeline (separate)

`benchmarks/` contains the offline evaluation pipeline for the
CIC-DDoS2019 flow-level dataset.  It trains Random Forest, Isolation Forest,
and Gaussian Naive Bayes classifiers.

**This pipeline is completely separate from the live pipeline.**
Flow-level features and HTTP-window features are different schemas and are
not interchangeable.  See `benchmarks/README.md` for details.
