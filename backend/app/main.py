"""
CLOUDSHIELD Backend — FastAPI application entry point.

Owner: Member 3 (backend core).

Responsibilities:
  - Create the FastAPI app instance.
  - Register exception handlers, CORS middleware, and the API router.
  - Run database table creation at startup.
  - Optionally start the pipeline scheduler (only when PIPELINE_ENABLED=true).
  - Mount the WebSocket endpoint.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import create_all_tables
from app.core.errors import AppError, app_error_handler, http_exception_handler
from app.core.logging import configure_logging

settings = get_settings()

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------ #
# Lifespan
# ------------------------------------------------------------------ #


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan handler.

    Startup:
      1. Configure logging.
      2. Create database tables (dev convenience, replace with Alembic in prod).
      3. Start the pipeline scheduler if PIPELINE_ENABLED=true.

    Shutdown:
      1. Stop the scheduler cleanly.
    """
    configure_logging(settings.LOG_LEVEL)
    logger.info(
        "Starting %s v%s (env=%s)",
        settings.APP_NAME, settings.APP_VERSION, settings.APP_ENV,
    )

    create_all_tables()
    logger.info("Database tables verified / created.")

    scheduler = None
    if settings.PIPELINE_ENABLED:
        from app.orchestrator.scheduler import PipelineScheduler  # noqa: PLC0415

        scheduler = PipelineScheduler()
        await scheduler.start()
        logger.info("Pipeline scheduler started (window=%ds).", settings.WINDOW_SECONDS)
    else:
        logger.info(
            "Pipeline disabled (PIPELINE_ENABLED=false). "
            "Set to true once stubs are implemented."
        )

    yield

    if scheduler is not None:
        await scheduler.stop()
        logger.info("Pipeline scheduler stopped.")

    logger.info("CLOUDSHIELD backend shut down.")


# ------------------------------------------------------------------ #
# App factory
# ------------------------------------------------------------------ #


def create_app() -> FastAPI:
    """
    Build and return the configured FastAPI application.

    Separating construction from module-level instantiation makes the app
    testable: tests import this function and pass a temporary database URL.
    """
    _settings = get_settings()

    application = FastAPI(
        title=_settings.APP_NAME,
        version=_settings.APP_VERSION,
        description=(
            "Security controller for cloud-hosted web services. "
            "Detects DDoS traffic, applies mitigation, and automates recovery."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # CORS — allow the React dashboard (member 4) during development.
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    application.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
    application.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore[arg-type]

    # API router (REST + WebSocket)
    from app.api.router import api_router  # noqa: PLC0415

    application.include_router(api_router, prefix=_settings.API_PREFIX)

    # WebSocket endpoint (outside the versioned prefix so the URL stays stable)
    from app.api.websocket import ws_router  # noqa: PLC0415

    application.include_router(ws_router)

    return application


# ------------------------------------------------------------------ #
# Module-level app instance used by uvicorn
# ------------------------------------------------------------------ #

app: FastAPI = create_app()
