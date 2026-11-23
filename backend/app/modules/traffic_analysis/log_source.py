"""
Nginx access log source — stub implementation.

Owner: Member 1.
# TODO(member1): implement NginxLogSource to tail NGINX_ACCESS_LOG_PATH
"""

from __future__ import annotations

from app.modules.traffic_analysis.interfaces import LogSource
from app.schemas.traffic import RequestLogRecord


class NginxLogSource(LogSource):
    """
    Reads new log records by tailing the Nginx access log file.

    Args:
        log_path: Absolute path to the Nginx access log
                  (from ``Settings.NGINX_ACCESS_LOG_PATH``).

    TODO(member1):
      - Open the file and seek to its end on first call.
      - On subsequent calls, read all new lines since the last position.
      - Delegate each line to a ``LogParser`` instance.
      - Handle log rotation (the file may be replaced without warning).
    """

    def __init__(self, log_path: str) -> None:
        self._log_path = log_path

    def read_new_records(self) -> list[RequestLogRecord]:
        """
        Return all log records added since the last call.

        Raises:
            NotImplementedError: TODO(member1): tail NGINX_ACCESS_LOG_PATH
                                 and parse new lines via NginxLogParser.
        """
        raise NotImplementedError(
            "TODO(member1): tail NGINX_ACCESS_LOG_PATH and parse new lines via NginxLogParser"
        )
