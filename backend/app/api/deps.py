"""
FastAPI dependency functions shared across routers.

Owner: Member 3 (backend core).

Usage::

    from app.api.deps import get_db_session, get_settings_dep

    @router.get("/example")
    def example(db: Session = Depends(get_db_session)):
        ...
"""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.database import get_db


def get_db_session() -> Generator[Session, None, None]:
    """
    Yield a database session for the duration of a request.

    Delegates to ``core.database.get_db`` so routers only need to import
    from ``app.api.deps``.
    """
    yield from get_db()


def get_settings_dep() -> Settings:
    """Return the cached application settings (useful for testing overrides)."""
    return get_settings()
