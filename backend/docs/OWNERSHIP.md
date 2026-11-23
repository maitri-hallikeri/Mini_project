# Ownership

## Team table

| Member | Role | Owns |
|---|---|---|
| Member 1 | Network data & traffic analysis | `app/modules/traffic_analysis/`, `benchmarks/cic_ddos2019_loader.py` |
| Member 2 | Detection, mitigation & recovery | `app/modules/detection/`, `app/modules/mitigation/`, `app/modules/recovery/`, `benchmarks/train_evaluate.py` |
| Member 3 | Backend core | `app/main.py`, `app/core/`, `app/schemas/`, `app/models/`, `app/repositories/`, `app/api/`, `app/orchestrator/`, Docker files, `tests/` |
| Member 4 | Frontend | React dashboard (separate repository); depends on `docs/API_CONTRACT.md` |

## Who to ask

| Topic | Ask |
|---|---|
| Nginx log format, feature computation | Member 1 (`@member1-username`) |
| Detection thresholds, mitigation policy, recovery logic | Member 2 (`@member2-username`) |
| API changes, schema changes, database schema, Docker | Member 3 (`@member3-username`) |
| Dashboard layout, WebSocket events, frontend build | Member 4 (`@member4-username`) |
| Any cross-cutting schema change | PR review required by all affected owners (see `MODULE_CONTRACTS.md`) |

## GitHub usernames (fill in)

| Member | GitHub username |
|---|---|
| Member 1 | `@member1-username` |
| Member 2 | `@member2-username` |
| Member 3 | `@member3-username` |
| Member 4 | `@member4-username` |
