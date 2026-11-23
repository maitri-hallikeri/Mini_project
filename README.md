# Mini Project

## Repository layout

```
Mini_project/
├── backend/                  # Security controller backend (Member 3 — this task)
│   ├── app/                  # FastAPI application
│   │   ├── core/             # Config, logging, database, error handling
│   │   ├── schemas/          # Shared Pydantic v2 contracts (all members depend on these)
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── repositories/     # Database CRUD layer
│   │   ├── api/              # REST routers + WebSocket
│   │   ├── orchestrator/     # Pipeline, scheduler, event bus
│   │   └── modules/          # Detection, mitigation, recovery, traffic analysis stubs
│   ├── benchmarks/           # Offline CIC-DDoS2019 evaluation pipeline
│   ├── tests/                # Pytest suite
│   └── docs/                 # Architecture, API contract, ownership docs
└── protection_engine/        # Member 2's earlier protection/recovery prototype
                              # (branch: feature/protection-recovery — do not modify)
```

See `backend/README.md` for quick-start instructions and `backend/docs/` for full documentation.
