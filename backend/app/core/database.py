"""
SQLAlchemy 2.0 engine and session factory.

Owner: Member 3 (backend core).

Supports SQLite (development default) and PostgreSQL (production).
Switch databases by changing DATABASE_URL in .env — no other code changes needed.

Usage::

    from app.core.database import get_db

    # In a FastAPI route:
    def my_route(db: Session = Depends(get_db)):
        ...
"""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

_settings = get_settings()


def _make_engine():
    """
    Build the SQLAlchemy engine for the configured DATABASE_URL.

    SQLite requires ``check_same_thread=False`` when used with FastAPI
    because requests can be served from different threads.  PostgreSQL does
    not need this argument, so it is applied only for SQLite connections.
    """
    url: str = _settings.DATABASE_URL
    connect_args: dict = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    engine = create_engine(
        url,
        connect_args=connect_args,
        # Echo SQL to stdout only in debug mode to keep logs clean.
        echo=(_settings.LOG_LEVEL == "DEBUG"),
    )

    # Enable WAL mode for SQLite — better read/write concurrency.
    if url.startswith("sqlite"):

        @event.listens_for(engine, "connect")
        def _set_wal(dbapi_conn, _connection_record):  # noqa: ANN001
            dbapi_conn.execute("PRAGMA journal_mode=WAL")

    return engine


engine = _make_engine()

SessionLocal: sessionmaker[Session] = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a SQLAlchemy session and closes it after
    the request finishes.

    Usage::

        from fastapi import Depends
        from sqlalchemy.orm import Session
        from app.core.database import get_db

        @router.get("/example")
        def example(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_all_tables() -> None:
    """
    Create all ORM-mapped tables in the database if they do not yet exist.

    Called once at application startup (``app/main.py`` lifespan).
    This is a development convenience; replace with Alembic migrations before
    going to production.
    """
    # Import here to avoid circular imports at module load time.
    from app.models.base import Base  # noqa: PLC0415

    Base.metadata.create_all(bind=engine)
