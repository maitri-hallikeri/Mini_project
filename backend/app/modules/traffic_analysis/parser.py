"""
Nginx access log parser — stub implementation.

Owner: Member 1.
# TODO(member1): implement NginxLogParser to parse combined log format
"""

from __future__ import annotations

from app.modules.traffic_analysis.interfaces import LogParser
from app.schemas.traffic import RequestLogRecord


class NginxLogParser(LogParser):
    """
    Parses lines in Nginx's default ``combined`` log format::

        $remote_addr - $remote_user [$time_local] "$request" $status
        $body_bytes_sent "$http_referer" "$http_user_agent"
        $request_time $upstream_addr

    TODO(member1):
      - Write a regex or split-based parser for the combined format.
      - Convert ``$time_local`` to a UTC-aware datetime.
      - Extract ``method`` and ``path`` from the ``$request`` field.
      - Return ``None`` for malformed or empty lines rather than raising.
    """

    def parse_line(self, line: str) -> RequestLogRecord | None:
        """
        Parse one raw Nginx log line.

        Raises:
            NotImplementedError: TODO(member1): parse Nginx combined log format line.
        """
        raise NotImplementedError(
            "TODO(member1): parse Nginx combined log format line into RequestLogRecord"
        )
