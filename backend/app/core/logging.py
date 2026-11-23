"""
Structured logging configuration for the CLOUDSHIELD backend.

Owner: Member 3 (backend core).
Call `configure_logging()` once at application startup (in main.py lifespan).
All modules obtain their logger via `logging.getLogger(__name__)`.
"""

from __future__ import annotations

import logging
import sys


def configure_logging(level: str = "INFO") -> None:
    """
    Configure the root logger with a consistent format.

    Args:
        level: One of DEBUG, INFO, WARNING, ERROR, CRITICAL.
               Passed directly from ``Settings.LOG_LEVEL``.
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(numeric_level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(numeric_level)

    # Avoid duplicate handlers if called more than once (e.g. in tests).
    if not root.handlers:
        root.addHandler(handler)
    else:
        root.handlers.clear()
        root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """
    Convenience wrapper; equivalent to ``logging.getLogger(name)``.

    Usage::

        from app.core.logging import get_logger
        logger = get_logger(__name__)
    """
    return logging.getLogger(name)
