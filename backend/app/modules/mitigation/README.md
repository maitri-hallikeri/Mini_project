# mitigation — Module README

**Owner:** Member 2

---

## Purpose

This module receives a `RiskAssessment` from the detection engine, decides
which protective actions to take, writes those rules to Nginx, records every
decision in the audit log, and later expires or rolls back actions.

---

## Inputs

| Source | Type |
|---|---|
| `detection.engine.DetectionEngine` | `RiskAssessment` (via orchestrator) |
| `orchestrator.Pipeline` | `now: datetime` for expiry sweep |

## Outputs

| Destination | Type |
|---|---|
| Nginx config file | deny / rate-limit rules |
| `repositories.mitigations` | `MitigationAction` |
| `repositories.audit` | `AuditRecord` |
| `orchestrator.Pipeline` | `list[MitigationAction]` (applied and expired) |

---

## Default risk-to-action policy

| Risk level | Actions |
|---|---|
| LOW | `LOG_ONLY` — record event, no traffic change |
| MEDIUM | `INCREASE_MONITORING` + conservative `RATE_LIMIT` |
| HIGH | `RATE_LIMIT` + `PROTECT_ENDPOINT` for targeted path |
| CRITICAL | `TEMP_BLOCK_IP` for high-confidence offenders + alert |

**Every action except LOG_ONLY must have a non-null `expires_at`.**
TTL defaults to `Settings.MITIGATION_DEFAULT_TTL_S` (default 300 s).

---

## File map

| File | Class | Responsibility |
|---|---|---|
| `interfaces.py` | `MitigationController`, `RuleWriter`, `AuditLogger` | Abstract contracts |
| `controller.py` | `DefaultMitigationController` | Decision + apply + expire + rollback |
| `nginx_writer.py` | `NginxRuleWriter` | Write deny / rate-limit Nginx includes |
| `expiry.py` | `find_expired()` | Helper: find ACTIVE actions past TTL |
| `audit.py` | `DbAuditLogger` | Persist audit records |

---

## TODO checklist

- [ ] `DefaultMitigationController.decide()` — risk-to-action policy  
      (adapt from `protection_engine/app/mitigation.py MitigationManager.evaluate_and_mitigate`)
- [ ] `DefaultMitigationController.apply()` — call `NginxRuleWriter`
- [ ] `DefaultMitigationController.expire_due()` — scan and expire
- [ ] `DefaultMitigationController.rollback()` — reverse + audit
- [ ] `NginxRuleWriter.write_blocklist()` — deny rules (adapt from `protection_engine/app/main.py sync_nginx_blocklist`)
- [ ] `NginxRuleWriter.write_rate_limits()` — rate-limit include file
- [ ] `NginxRuleWriter.reload()` — nginx -s reload
- [ ] `DbAuditLogger.record()` — persist via AuditRepository
- [ ] Unit tests in `tests/modules/mitigation/`

---

## Schema contract

Schemas are in `app/schemas/mitigation.py` (owned by Member 3).
**Do not modify schemas without opening a PR approved by both Member 2 and Member 3.**
