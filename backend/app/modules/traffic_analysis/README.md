# traffic_analysis — Module README

**Owner:** Member 1

---

## Purpose

This module transforms raw Nginx access log lines into structured
`WindowFeatures` objects and maintains a learned baseline of normal traffic
for use by the detection engine.

---

## Inputs

| Source | Type |
|---|---|
| Nginx access log file | Raw text lines (combined log format) |
| `Settings.NGINX_ACCESS_LOG_PATH` | Path to log file |
| `Settings.WINDOW_SECONDS` | Width of each aggregation window |

## Outputs

| Destination | Type |
|---|---|
| `detection.engine.DetectionEngine` | `WindowFeatures` |
| `detection.engine.DetectionEngine` | `BaselineProfile` |
| `repositories.windows.WindowRepository` | `WindowFeatures` (via orchestrator) |

---

## File map

| File | Class | Responsibility |
|---|---|---|
| `interfaces.py` | `LogSource`, `LogParser`, `WindowAggregator`, `FeatureExtractor`, `BaselineStore` | Abstract contracts |
| `log_source.py` | `NginxLogSource` | Tail the Nginx access log |
| `parser.py` | `NginxLogParser` | Parse one log line → `RequestLogRecord` |
| `windowing.py` | `FixedWindowAggregator` | Bucket records into time windows |
| `features.py` | `WindowFeatureExtractor` | Compute all `WindowFeatures` fields |
| `baseline.py` | `InMemoryBaselineStore` | Rolling per-hour-bucket statistics |

---

## TODO checklist

- [ ] `NginxLogParser.parse_line()` — regex for combined log format
- [ ] `FixedWindowAggregator.add()` / `pop_ready_windows()` — bucketing logic
- [ ] `WindowFeatureExtractor.extract()` — all 15 feature fields
  - `total_requests`, `requests_per_sec`
  - `unique_ips`, `top_ip`, `top_ip_share`, `max_requests_per_ip`, `mean_requests_per_ip`
  - `top_endpoint`, `top_endpoint_share`
  - `status_4xx_rate`, `status_5xx_rate`
  - `avg_latency_ms`, `p95_latency_ms`
  - `burstiness` (coefficient of variation of per-second counts)
- [ ] `InMemoryBaselineStore.get()` / `update()` — Welford incremental mean/std
- [ ] `NginxLogSource.read_new_records()` — file tail with rotation handling
- [ ] Unit tests in `tests/modules/traffic_analysis/`

---

## Schema contract

Schemas are defined in `app/schemas/traffic.py` (owned by Member 3).
**Do not modify schemas without opening a PR approved by both Member 1 and Member 3.**
