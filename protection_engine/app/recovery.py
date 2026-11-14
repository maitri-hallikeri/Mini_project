import time
from datetime import datetime
from typing import Dict, List, Optional
import docker
from docker.errors import DockerException, NotFound

from app.config import settings
from app.schemas import ContainerHealthRecord


class RecoveryManager:
    """
    Monitors Docker application instances, detects unhealthy/crashed containers,
    triggers automated container restarts, verifies recovery, and logs recovery time.
    """

    def __init__(self):
        # Connect to local Docker Desktop / Docker Engine if running
        try:
            self.docker_client = docker.from_env()
            self.docker_available = True
        except DockerException:
            self.docker_client = None
            self.docker_available = False

        # Track consecutive failure counts per container
        self.failure_counts: Dict[str, int] = {
            name: 0 for name in settings.TARGET_CONTAINERS
        }

        # Store latest health status of each container
        self.container_statuses: Dict[str, ContainerHealthRecord] = {}

        # Audit history of all recovery events (for Person 4's Dashboard & Module F metrics)
        self.recovery_history: List[dict] = []

        # Simulation state (used only if Docker Desktop is not running during unit tests)
        self.simulated_unhealthy: set[str] = set()

    def _is_container_healthy(self, container_name: str) -> tuple[bool, str]:
        """
        Checks whether a container is running and healthy.
        Returns (is_healthy: bool, detail_message: str).
        """
        # Mode 1: Real Docker Engine is connected
        if self.docker_available and self.docker_client:
            try:
                container = self.docker_client.containers.get(container_name)
                container.reload()  # Refresh status from Docker daemon
                state = container.status  # e.g., 'running', 'exited', 'restarting'

                if state == "running":
                    return True, "Container is running normally."
                return False, f"Container state is '{state}' (expected 'running')."

            except NotFound:
                return False, f"Container '{container_name}' not found in Docker."
            except DockerException as e:
                return False, f"Docker error checking container: {str(e)}"

        # Mode 2: Safe Simulation Fallback (when Docker Desktop is closed)
        if container_name in self.simulated_unhealthy:
            return False, "Simulated container crash/unresponsive state."
        return True, "Healthy (Simulation Mode — Docker Desktop not active)."

    def _restart_container(self, container_name: str) -> tuple[bool, float, str]:
        """
        Executes automated container restart and measures recovery duration.
        Returns (success: bool, recovery_time_seconds: float, message: str).
        """
        start_time = time.perf_counter()

        # Mode 1: Real Docker Restart
        if self.docker_available and self.docker_client:
            try:
                container = self.docker_client.containers.get(container_name)
                container.restart(timeout=10)
                container.reload()

                elapsed = round(time.perf_counter() - start_time, 3)
                if container.status == "running":
                    return True, elapsed, f"Container restarted and verified running in {elapsed}s."
                return False, elapsed, f"Restart executed, but state is '{container.status}'."

            except Exception as e:
                elapsed = round(time.perf_counter() - start_time, 3)
                return False, elapsed, f"Automated restart failed: {str(e)}"

        # Mode 2: Simulation Mode Restart
        time.sleep(0.2)  # Simulate brief restart delay
        self.simulated_unhealthy.discard(container_name)
        elapsed = round(time.perf_counter() - start_time, 3)
        return True, elapsed, f"Simulated container recovery completed in {elapsed}s."

    def check_and_recover_all(self) -> List[ContainerHealthRecord]:
        """
        Runs one health-check sweep across all configured target containers.
        Automatically triggers recovery if consecutive failures reach FAILURE_THRESHOLD.
        """
        now = datetime.utcnow()
        results: List[ContainerHealthRecord] = []

        for name in settings.TARGET_CONTAINERS:
            is_healthy, detail = self._is_container_healthy(name)

            if is_healthy:
                # Reset failure counter on healthy heartbeat
                self.failure_counts[name] = 0
                prev = self.container_statuses.get(name)

                record = ContainerHealthRecord(
                    container_name=name,
                    status="HEALTHY",
                    consecutive_failures=0,
                    last_checked_at=now,
                    last_recovery_at=prev.last_recovery_at if prev else None,
                    recovery_time_seconds=prev.recovery_time_seconds if prev else None,
                    message=detail,
                )
            else:
                # Increment consecutive failures
                self.failure_counts[name] = self.failure_counts.get(name, 0) + 1
                fails = self.failure_counts[name]

                if fails >= settings.FAILURE_THRESHOLD:
                    # Threshold reached — trigger automated recovery!
                    success, recovery_time, rec_msg = self._restart_container(name)
                    recovery_timestamp = datetime.utcnow()

                    self.recovery_history.append({
                        "container_name": name,
                        "triggered_at": now.isoformat(),
                        "recovered_at": recovery_timestamp.isoformat(),
                        "recovery_time_seconds": recovery_time,
                        "success": success,
                        "details": rec_msg,
                    })

                    if success:
                        self.failure_counts[name] = 0
                        record = ContainerHealthRecord(
                            container_name=name,
                            status="HEALTHY",
                            consecutive_failures=0,
                            last_checked_at=recovery_timestamp,
                            last_recovery_at=recovery_timestamp,
                            recovery_time_seconds=recovery_time,
                            message=f"RECOVERED: {rec_msg}",
                        )
                    else:
                        record = ContainerHealthRecord(
                            container_name=name,
                            status="FAILED",
                            consecutive_failures=fails,
                            last_checked_at=recovery_timestamp,
                            message=f"RECOVERY FAILED: {rec_msg}",
                        )
                else:
                    # Unhealthy, but waiting to confirm threshold before restarting
                    record = ContainerHealthRecord(
                        container_name=name,
                        status="UNHEALTHY",
                        consecutive_failures=fails,
                        last_checked_at=now,
                        message=f"Warning ({fails}/{settings.FAILURE_THRESHOLD} fails): {detail}",
                    )

            self.container_statuses[name] = record
            results.append(record)

        return results


# Shared singleton instance
recovery_manager = RecoveryManager()