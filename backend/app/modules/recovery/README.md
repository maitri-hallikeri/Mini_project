# recovery — Module README

**Owner:** Member 2

---

## Purpose

This module monitors the health of each application replica, detects
consecutive failures, triggers automated recovery (restart or reroute),
and restores replicas to the routing pool once they are healthy again.

---

## Inputs

| Source | Type |
|---|---|
| `Settings.REPLICA_URLS` | List of replica base URLs to poll |
| `Settings.HEALTH_CHECK_INTERVAL_S` | Poll interval |
| `orchestrator.Pipeline` | Triggered every pipeline cycle |

## Outputs

| Destination | Type |
|---|---|
| `orchestrator.Pipeline` | `list[ReplicaHealth]` |
| `orchestrator.Pipeline` | `list[RecoveryEvent]` |
| `repositories` | Recovery events (via orchestrator) |

---

## Recovery policy

1. After `FAILURE_THRESHOLD` consecutive failed health checks → `RESTART`.
2. If restart fails → `REMOVE_FROM_ROUTING`.
3. When healthy checks resume → `RESTORE_ROUTING`.

The `failure_threshold` value should come from `Settings` (not hard-coded).
Adapt the existing `protection_engine/app/config.py FAILURE_THRESHOLD`.

---

## File map

| File | Class | Responsibility |
|---|---|---|
| `interfaces.py` | `HealthChecker`, `RecoveryManager` | Abstract contracts |
| `health_checker.py` | `HttpHealthChecker` | HTTP probe each replica |
| `recovery_manager.py` | `DefaultRecoveryManager` | Restart / reroute logic |

---

## TODO checklist

- [ ] `HttpHealthChecker.check_all()` — HTTP GET + latency measurement  
      (adapt from `protection_engine/app/recovery.py _is_container_healthy`)
- [ ] `DefaultRecoveryManager.recover()` — restart / reroute logic  
      (adapt from `protection_engine/app/recovery.py check_and_recover_all`)
- [ ] `DefaultRecoveryManager.restore_routing()` — Nginx upstream restore
- [ ] Add `FAILURE_THRESHOLD` to `Settings` (coordinate with Member 3)
- [ ] Unit tests in `tests/modules/recovery/`

---

## Schema contract

Schemas are in `app/schemas/recovery.py` (owned by Member 3).
**Do not modify schemas without opening a PR approved by both Member 2 and Member 3.**

## Differences from `protection_engine/app/recovery.py`

| Old | New |
|---|---|
| Docker SDK (`docker.from_env()`) | HTTP probe via `httpx` |
| `ContainerHealthRecord` schema | `ReplicaHealth` schema |
| `recovery_manager` singleton | Injected via `Pipeline.__init__` |
