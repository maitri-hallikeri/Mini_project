
from __future__ import annotations

import os

from app.modules.traffic_analysis.interfaces import LogSource
from app.modules.traffic_analysis.parser import NginxLogParser
from app.schemas.traffic import RequestLogRecord


class NginxLogSource(LogSource):
    """
    Reads newly appended Nginx access-log entries and parses them.
    """

    def __init__(self, log_path: str) -> None:
        self._log_path = log_path
        self._parser = NginxLogParser()

        self._file = None
        self._file_identity = None
        self._position = 0
        self._pending = b""

    def read_new_records(self) -> list[RequestLogRecord]:
        try:
            file_stat = os.stat(self._log_path)
        except FileNotFoundError:
            return []

        current_identity = (
            file_stat.st_dev,
            file_stat.st_ino,
        )

        # First call: open the existing file and start at its end.
        if self._file is None:
            self._file = open(self._log_path, "rb")
            self._file.seek(0, os.SEEK_END)

            self._position = self._file.tell()
            self._file_identity = current_identity

            return []

        # Detect log rotation or replacement.
        if current_identity != self._file_identity:
            self._file.close()
            self._file = open(self._log_path, "rb")

            self._file_identity = current_identity
            self._position = 0
            self._pending = b""

        # Detect truncation of the same file.
        elif file_stat.st_size < self._position:
            self._file.seek(0)
            self._position = 0
            self._pending = b""

        # Read only newly appended data.
        self._file.seek(self._position)
        new_data = self._file.read()
        self._position = self._file.tell()

        if not new_data:
            return []

        # Preserve incomplete lines until the next read.
        data = self._pending + new_data
        lines = data.splitlines(keepends=True)

        self._pending = b""
        complete_lines = []

        for line in lines:
            if line.endswith((b"\n", b"\r")):
                complete_lines.append(line)
            else:
                self._pending = line

        records = []

        for line in complete_lines:
            text_line = line.decode("utf-8", errors="replace").strip()

            if not text_line:
                continue

            record = self._parser.parse_line(text_line)

            if record is not None:
                records.append(record)

        records.sort(key=lambda record: record.timestamp)

        return records

    def close(self) -> None:
        """Close the currently open log file."""
        if self._file is not None:
            self._file.close()
            self._file = None
