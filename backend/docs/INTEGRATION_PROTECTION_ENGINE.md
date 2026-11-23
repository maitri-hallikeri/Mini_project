# Integration: protection_engine → backend

This document maps the existing `protection_engine/` prototype
(branch `feature/protection-recovery`) to the new backend scaffold.
It lists overlaps, schema differences, and the adaptation work Member 2
must do before closing the prototype's API surface.

> **Note:** `protection_engine/` was present in the working tree at the time
> this scaffold was created.  Its contents were read (read-only) and are
> documented here.  **Nothing inside `protection_engine/` was modified.**

---

## File mapping

| protection_engine file | New backend location | Notes |
|---|---|---|
| `app/mitigation.py` | `app/modules/mitigation/controller.py` | `MitigationManager` → `DefaultMitigationController`; see §Schema differences |
| `app/recovery.py` | `app/modules/recovery/health_checker.py` + `recovery_manager.py` | Split into two classes; Docker SDK → HTTP probe |
| `app/decision_engine.py` | `app/modules/detection/` (empty in prototype) | Member 2 implements from scratch in `rules.py`, `statistical.py`, `engine.py` |
| `app/schemas.py` | `app/schemas/` (all 6 files) | Superset; see §Schema differences |
| `app/database.py` | `app/core/database.py` (empty in prototype) | Fully implemented in new scaffold |
| `app/config.py` | `app/core/config.py` | Settings merged and extended; see §Config differences |
| `app/logger.py` | `app/core/logging.py` (empty in prototype) | Fully implemented in new scaffold |
| `app/main.py` | `app/main.py` + `app/api/routers/` | Routes re-architected under versioned prefix `/api/v1` |
| `requirements.txt` | `requirements.txt` | `docker` dependency removed (not needed in new backend) |
| `nginx_blocked_ips.conf` | Managed by `NginxRuleWriter` at runtime | Not committed; path in `Settings.NGINX_BLOCKLIST_PATH` |
| `tests/` | `tests/` | Existing tests remain in `protection_engine/tests/`; new tests in `backend/tests/` |

---

## Schema differences

### RiskLevel

| Prototype (`schemas.py`) | New (`schemas/detection.py`) | Action |
|---|---|---|
| `LOW, MEDIUM, HIGH, CRITICAL` | `LOW, MEDIUM, HIGH, CRITICAL` | ✅ Identical |

### Attack scenario

| Prototype | New | Action |
|---|---|---|
| `AttackType` enum (6 values incl. `HTTP_FLOOD`, `DISTRIBUTED_HTTP_FLOOD`, `LOW_RATE_PERSISTENT`, `MIXED_BOT_BURST`) | `Scenario` enum (5 values: `NONE, REQUEST_FLOOD, ENDPOINT_FLOOD, BURST_ANOMALY, UNKNOWN`) | ⚠️ **Member 2:** map `HTTP_FLOOD`/`DISTRIBUTED_HTTP_FLOOD` → `REQUEST_FLOOD`; `TARGETED_ENDPOINT_FLOOD` → `ENDPOINT_FLOOD`; `SINGLE_SOURCE_BURST` → `BURST_ANOMALY`; `LOW_RATE_PERSISTENT`/`MIXED_BOT_BURST` → `UNKNOWN` |

### Mitigation action

| Prototype `MitigationRecord` field | New `MitigationAction` field | Action |
|---|---|---|
| `action_id: str` (8-char) | `id: str` (UUID v4) | ⚠️ Use `uuid.uuid4()` |
| `source_ip: str` | `target: str \| None` | ⚠️ Rename; target may also be an endpoint |
| `action_taken: ProtectionAction` | `action_type: ActionType` | ⚠️ Map: `TEMPORARY_BLOCK` → `TEMP_BLOCK_IP`; `RATE_LIMIT` → `RATE_LIMIT`; `ALLOW` → `LOG_ONLY` |
| `is_active: bool` | `status: ActionStatus` | ⚠️ Map: `is_active=True` → `ACTIVE`; `False` → `EXPIRED` |
| `attack_type: AttackType` | (not stored in `MitigationAction`) | Stored in `RiskAssessment.scenario` instead |
| — | `expires_at: UTCDatetime \| None` | ✅ Already present as `expires_at` in prototype |

### Recovery / health

| Prototype `ContainerHealthRecord` | New `ReplicaHealth` | Action |
|---|---|---|
| `container_name: str` | `replica_id: str` | ⚠️ Rename |
| `status: str` ("HEALTHY", "UNHEALTHY", …) | `healthy: bool` + `consecutive_failures` | ⚠️ Map: "HEALTHY" → `healthy=True, consecutive_failures=0` |
| `last_checked_at: datetime` | `last_checked: UTCDatetime` | ⚠️ Rename + ensure UTC |
| `recovery_time_seconds: float \| None` | Stored in `RecoveryEvent.details["recovery_time_s"]` | ⚠️ Move to details dict |

---

## Config differences

| Prototype `Settings` field | New `Settings` field | Notes |
|---|---|---|
| `MEDIUM_RISK_LIMIT_SECONDS` | `MITIGATION_DEFAULT_TTL_S` | Generalised TTL; set to 120 for MEDIUM |
| `HIGH_RISK_BLOCK_SECONDS` | `MITIGATION_DEFAULT_TTL_S` | Per-level TTL logic moved to controller |
| `CRITICAL_RISK_BLOCK_SECONDS` | `MITIGATION_DEFAULT_TTL_S` | Same |
| `WHITELISTED_IPS` | Not in new config | ⚠️ **Member 2:** add `WHITELISTED_IPS` to `Settings` if needed |
| `HEALTH_CHECK_INTERVAL_SECONDS` | `HEALTH_CHECK_INTERVAL_S` | Renamed |
| `FAILURE_THRESHOLD` | Not yet in new config | ⚠️ **Member 2:** add to `Settings` |
| `TARGET_CONTAINERS` | `REPLICA_URLS` | Renamed; now URL-based, not Docker container names |

---

## Adaptation TODO for Member 2

- [ ] `controller.py DefaultMitigationController.decide()` — port risk-to-action policy from `protection_engine/app/mitigation.py MitigationManager.evaluate_and_mitigate()`
- [ ] `controller.py DefaultMitigationController.expire_due()` — port `cleanup_expired_restrictions()` logic
- [ ] `nginx_writer.py NginxRuleWriter.write_blocklist()` — port `protection_engine/app/main.py sync_nginx_blocklist()`
- [ ] `health_checker.py HttpHealthChecker.check_all()` — replace Docker SDK with `httpx` HTTP probe
- [ ] `recovery_manager.py DefaultRecoveryManager.recover()` — port `check_and_recover_all()` threshold + restart logic
- [ ] Map old `AttackType` enum to new `Scenario` enum values
- [ ] Map old `MitigationRecord` fields to new `MitigationAction` fields
- [ ] Add `WHITELISTED_IPS` and `FAILURE_THRESHOLD` to `app/core/config.py Settings`

---

## Background monitor loop

The prototype's `background_monitor_loop()` in `main.py` (Nginx sync +
health check every 5 s) is replaced by `app/orchestrator/scheduler.py
PipelineScheduler`, which calls `Pipeline.run_cycle()` on the
`WINDOW_SECONDS` interval.  Steps 7 (expire actions), 9 (check health),
and 10 (recover) in `run_cycle()` are the direct replacements.
