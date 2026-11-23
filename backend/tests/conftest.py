"""
Shared pytest fixtures for the CLOUDSHIELD backend test suite.

Owner: Member 3 (backend core).

Fixtures:
  client     — HTTPX TestClient backed by a fresh in-memory SQLite database.
  db_session — Raw SQLAlchemy Session for the in-memory database (repo tests).
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import get_db
from app.models.base import Base

# ------------------------------------------------------------------ #
# In-memory SQLite engine for tests (isolated, torn down after each test)
# ------------------------------------------------------------------ #

TEST_DATABASE_URL = "sqlite://"  # pure in-memory, no file


@pytest.fixture(scope="function")
def db_engine():
    """Create a fresh in-memory SQLite engine for one test function."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Yield a SQLAlchemy Session connected to the in-memory test database."""
    TestSessionLocal = sessionmaker(bind=db_engine, autocommit=False, autoflush=False)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_engine):
    """
    HTTPX TestClient wired to a fresh in-memory database.

    The ``get_db`` dependency is overridden so every request uses the
    test-scoped engine instead of the real database.
    """
    # Patch settings to use in-memory SQLite and disable the pipeline.
    import os  # noqa: PLC0415

    from app.main import create_app  # noqa: PLC0415

    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    os.environ["PIPELINE_ENABLED"] = "false"

    # Clear the lru_cache so the patched env is picked up.
    from app.core.config import get_settings  # noqa: PLC0415

    get_settings.cache_clear()

    # Rebuild the engine with the patched settings.
    from app.core import database as db_module  # noqa: PLC0415

    db_module.engine = db_engine
    db_module.SessionLocal = sessionmaker(
        bind=db_engine, autocommit=False, autoflush=False
    )

    application = create_app()

    # Override the get_db dependency.
    TestSessionLocal = sessionmaker(bind=db_engine, autocommit=False, autoflush=False)

    def _override_get_db():
        session = TestSessionLocal()
        try:
            yield session
        finally:
            session.close()

    application.dependency_overrides[get_db] = _override_get_db

    with TestClient(application, raise_server_exceptions=True) as c:
        yield c

    # Restore lru_cache after the test.
    get_settings.cache_clear()
