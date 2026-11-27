
from __future__ import annotations

import re
from datetime import datetime, timezone

from pydantic import ValidationError

from app.modules.traffic_analysis.interfaces import LogParser
from app.schemas.traffic import RequestLogRecord


class NginxLogParser(LogParser):

    LOG_PATTERN = re.compile(
        r'^(?P<remote_addr>\S+) \S+ \S+ '
        r'\[(?P<time_local>[^\]]+)\] '
        r'"(?P<request>[^"]*)" '
        r'(?P<status>\d{3}) '
        r'(?P<bytes_sent>\d+) '
        r'"(?P<referer>[^"]*)" '
        r'"(?P<user_agent>[^"]*)" '
        r'(?P<request_time>\S+) '
        r'(?P<upstream>\S+)$'
    )

    def parse_line(self, line: str) -> RequestLogRecord | None:

        if not line or not line.strip():
            return None

        match = self.LOG_PATTERN.match(line.strip())

        if not match:
            return None

        try:
            data = match.groupdict()

            timestamp = datetime.strptime(
                data["time_local"],
                "%d/%b/%Y:%H:%M:%S %z"
            ).astimezone(timezone.utc)

            request_parts = data["request"].split()

            if len(request_parts) != 3:
                return None

            method, target, _protocol = request_parts
            path = target.split("?", 1)[0]

            if not path:
                return None

            request_time_ms = float(data["request_time"]) * 1000

            upstream = data["upstream"]
            if upstream == "-":
                upstream = None

            user_agent = data["user_agent"]
            if user_agent == "-":
                user_agent = None

            return RequestLogRecord(
                timestamp=timestamp,
                remote_addr=data["remote_addr"],
                method=method,
                path=path,
                status=int(data["status"]),
                bytes_sent=int(data["bytes_sent"]),
                request_time_ms=request_time_ms,
                upstream=upstream,
                user_agent=user_agent,
            )

        except (ValueError, TypeError, ValidationError):
            return None
