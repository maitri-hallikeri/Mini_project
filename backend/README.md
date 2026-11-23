# CLOUDSHIELD Backend

Security controller for the CLOUDSHIELD cloud-hosted DDoS protection system.

## What it does

The backend continuously reads Nginx access logs, groups requests into
short time windows, extracts traffic features, runs a hybrid detector
(threshold rules + statistical anomaly + optional ML), produces an
explainable risk score, applies reversible mitigations through Nginx rules,
monitors replica health, and automates recovery — all served through a REST
API and a live WebSocket feed.

## Architecture (one paragraph)

An asyncio pipeline (`app/orchestrator/`) runs every `WINDOW_SECONDS` (default
10 s).  It calls the traffic analysis module (Member 1) to parse log records
and compute `WindowFeatures`, passes them to the detection engine (Member 2)
which runs `RuleDetector`, `StatisticalDetector`, and optionally `MLDetector`
to produce a `RiskAssessment`, then hands the assessment to the mitigation
controller (Member 2) which writes Nginx rules and records every action in an
audit log.  The recovery module (Member 2) polls each replica with HTTP health
probes and restarts or reroutes unhealthy ones.  The orchestrator persists all
data via SQLAlchemy repositories (Member 3) and broadcasts live events to
WebSocket clients (Member 4's dashboard).

## Quick start

```bash
cd backend
python -m venv .venv && .venv\Scripts\Activate.ps1  # Windows
pip install -r requirements-dev.txt
copy .env.example .env
uvicorn app.main:app --reload
# → http://localhost:8000/docs
```

See `docs/GETTING_STARTED.md` for the full guide.

## Run tests

```bash
pytest                 # all tests
pytest -v              # verbose
```

## Run linter

```bash
ruff check .
```

## Docker

```bash
docker compose up --build
```

## Documentation

| File | Contents |
|---|---|
| `docs/GETTING_STARTED.md` | Setup, run, test, Docker |
| `docs/ARCHITECTURE.md` | End-to-end flow diagram, module dependency graph |
| `docs/MODULE_CONTRACTS.md` | All interface signatures with inputs/outputs |
| `docs/API_CONTRACT.md` | All REST routes and WebSocket messages (for Member 4) |
| `docs/OWNERSHIP.md` | Who owns what; who to ask |
| `docs/INTEGRATION_PROTECTION_ENGINE.md` | Mapping from the `protection_engine/` prototype |
| `app/modules/*/README.md` | Per-module owner, purpose, TODO checklist |
| `benchmarks/README.md` | Offline CIC-DDoS2019 evaluation pipeline |
