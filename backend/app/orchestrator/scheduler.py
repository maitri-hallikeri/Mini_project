"""
Background scheduler that drives the pipeline loop.

Owner: Member 3 (backend core).

The scheduler starts only when ``PIPELINE_ENABLED=true`` (default: false).
This means the application boots and passes all tests without any module
stub raising ``NotImplementedError``.

When enabled, ``PipelineScheduler`` creates a ``Pipeline`` instance with
stub implementations and calls ``run_cycle()`` every ``WINDOW_SECONDS``.

TODO(member3): Replace the stub module constructors below with real
implementations once Members 1 and 2 have completed their modules.
"""

from __future__ import annotations

import asyncio
import logging

from app.core.config import get_settings
from app.orchestrator.event_bus import event_bus

logger = logging.getLogger(__name__)


class PipelineScheduler:
    """
    Runs the detection pipeline on a fixed interval in the background.

    Usage (called from ``app/main.py`` lifespan)::

        scheduler = PipelineScheduler()
        await scheduler.start()   # non-blocking
        ...
        await scheduler.stop()    # graceful shutdown
    """

    def __init__(self) -> None:
        self._settings = get_settings()
        self._task: asyncio.Task | None = None
        self._running = False

    async def start(self) -> None:
        """Launch the background loop as an asyncio task."""
        self._running = True
        self._task = asyncio.create_task(self._loop(), name="pipeline-scheduler")
        logger.info(
            "PipelineScheduler started (interval=%ds).",
            self._settings.WINDOW_SECONDS,
        )

    async def stop(self) -> None:
        """Cancel the background loop and wait for it to exit."""
        self._running = False
        if self._task is not None and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("PipelineScheduler stopped.")

    async def _loop(self) -> None:
        """
        Tick the pipeline every ``WINDOW_SECONDS``.

        Errors inside ``run_cycle()`` are caught and logged so that a single
        bad cycle does not crash the scheduler.
        """
        while self._running:
            try:
                pipeline = self._build_pipeline()
                await pipeline.run_cycle()
            except NotImplementedError as exc:
                # Expected until module stubs are implemented.
                logger.warning("Pipeline cycle skipped (not implemented): %s", exc)
            except Exception as exc:  # noqa: BLE001
                logger.exception("Pipeline cycle error: %s", exc)

            await asyncio.sleep(self._settings.WINDOW_SECONDS)

    def _build_pipeline(self):  # noqa: ANN201
        """
        Construct the ``Pipeline`` with all module dependencies.

        TODO(member3): Replace each stub constructor call below with the real
        implementation once Members 1 and 2 have completed their modules.
        Import the real classes and inject them here.
        """
        from app.orchestrator.pipeline import Pipeline  # noqa: PLC0415

        # --- Stub placeholders (all raise NotImplementedError when called) ---
        # TODO(member3): replace with real module instances, e.g.:
        #   from app.modules.traffic_analysis.log_source import NginxLogSource
        #   log_source = NginxLogSource(self._settings.NGINX_ACCESS_LOG_PATH)

        return Pipeline(
            log_source=None,
            window_aggregator=None,
            feature_extractor=None,
            baseline_store=None,
            detection_engine=None,
            mitigation_ctrl=None,
            health_checker=None,
            recovery_manager=None,
            window_repo=None,
            risk_repo=None,
            mitigation_repo=None,
            audit_repo=None,
            incident_repo=None,
            bus=event_bus,
        )
