# Getting Started

## Prerequisites

- Python 3.11 or later
- Git
- Docker Desktop (optional, for containerised run)

---

## 1. Create a virtual environment and install dependencies

```bash
cd backend
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

pip install -r requirements-dev.txt
```

If you need the ML benchmark pipeline (Members 1 and 2):

```bash
pip install -r requirements-ml.txt
```

---

## 2. Configure the environment

```bash
copy .env.example .env     # Windows
cp  .env.example .env      # macOS / Linux
```

Edit `.env` as needed.  The defaults work for local development with SQLite
and the pipeline disabled.

Key settings to review:

| Variable | Default | Notes |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./data/app.db` | Switch to PostgreSQL by changing this |
| `PIPELINE_ENABLED` | `false` | Set to `true` only after module stubs are implemented |
| `LOG_LEVEL` | `INFO` | Set to `DEBUG` to see SQL queries |

---

## 3. Run the development server

```bash
# From backend/
uvicorn app.main:app --reload
```

Open http://localhost:8000/docs — every route should be listed.

---

## 4. Run the test suite

```bash
# From backend/
pytest
```

Expected result: all tests pass, 4 tests skipped (module placeholder tests).

```bash
# Verbose output
pytest -v

# One file only
pytest tests/test_health.py -v
```

---

## 5. Run the linter

```bash
# From backend/
ruff check .
```

Expected result: no errors.

Auto-fix safe issues:

```bash
ruff check . --fix
```

---

## 6. Run with Docker Compose

```bash
# From backend/
docker compose up --build
```

The backend starts on port 8000.  The healthcheck polls `/api/v1/health`.

To use PostgreSQL instead of SQLite:

```bash
# Update .env:
# DATABASE_URL=postgresql://cloudshield:secret@postgres:5432/cloudshield

docker compose --profile postgres up --build
```

---

## 7. Explore the API

- **Interactive docs (Swagger UI):** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json
- **WebSocket live feed:** `ws://localhost:8000/ws/live`

---

## 8. Project layout quick reference

```
backend/
  app/
    core/           Config, logging, database, error handling
    schemas/        Pydantic v2 contracts (read these before coding)
    models/         SQLAlchemy ORM tables
    repositories/   Database CRUD stubs
    api/            REST routers + WebSocket
    orchestrator/   Pipeline, scheduler, event bus
    modules/        Member implementation areas
      traffic_analysis/   Member 1
      detection/          Member 2
      mitigation/         Member 2
      recovery/           Member 2
  benchmarks/       Offline CIC-DDoS2019 evaluation (Members 1 & 2)
  tests/            Pytest suite
  docs/             This folder
```
