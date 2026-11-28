
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.modules.traffic_analysis.baseline import InMemoryBaselineStore
from app.modules.traffic_analysis.features import WindowFeatureExtractor
from app.modules.traffic_analysis.log_source import NginxLogSource
from app.modules.traffic_analysis.parser import NginxLogParser
from app.modules.traffic_analysis.windowing import FixedWindowAggregator
from app.schemas.traffic import RequestLogRecord


def make_record(
    timestamp: datetime,
    ip: str = "192.168.1.10",
    path: str = "/products",
    status: int = 200,
    latency: float = 25.0,
) -> RequestLogRecord:
    return RequestLogRecord(
        timestamp=timestamp,
        remote_addr=ip,
        method="GET",
        path=path,
        status=status,
        bytes_sent=512,
        request_time_ms=latency,
        upstream="127.0.0.1:8080",
        user_agent="Mozilla/5.0",
    )


def make_nginx_line(
    ip: str = "192.168.1.10",
    timestamp: str = "23/Nov/2026:10:00:00 +0000",
    path: str = "/products?id=1",
    status: int = 200,
    request_time: str = "0.025",
) -> str:
    return (
        f'{ip} - - [{timestamp}] '
        f'"GET {path} HTTP/1.1" '
        f'{status} 512 "-" "Mozilla/5.0" '
        f'{request_time} 127.0.0.1:8080'
    )


# ---------------------------------------------------------
# 1. NGINX LOG PARSER
# ---------------------------------------------------------

def test_parser_extracts_valid_nginx_log():
    parser = NginxLogParser()

    record = parser.parse_line(make_nginx_line())

    assert record is not None
    assert record.remote_addr == "192.168.1.10"
    assert record.method == "GET"
    assert record.path == "/products"
    assert record.status == 200
    assert record.bytes_sent == 512
    assert record.request_time_ms == 25.0
    assert record.upstream == "127.0.0.1:8080"
    assert record.user_agent == "Mozilla/5.0"
    assert record.timestamp == datetime(2026, 11, 23, 10, 0, tzinfo=UTC)


def test_parser_removes_query_parameters():
    parser = NginxLogParser()

    record = parser.parse_line(
        make_nginx_line(path="/login?user=admin&id=10")
    )

    assert record is not None
    assert record.path == "/login"


def test_parser_handles_missing_optional_values():
    parser = NginxLogParser()

    line = (
        '192.168.1.20 - - [23/Nov/2026:10:00:00 +0000] '
        '"GET / HTTP/1.1" 200 0 "-" "-" 0.010 -'
    )

    record = parser.parse_line(line)

    assert record is not None
    assert record.upstream is None
    assert record.user_agent is None
    assert record.request_time_ms == 10.0


def test_parser_rejects_invalid_lines():
    parser = NginxLogParser()

    assert parser.parse_line("") is None
    assert parser.parse_line("invalid nginx log") is None
    assert parser.parse_line("127.0.0.1 - - [invalid]") is None


# ---------------------------------------------------------
# 2. NGINX LOG SOURCE
# ---------------------------------------------------------

def test_log_source_reads_only_newly_appended_records(tmp_path):
    log_file = tmp_path / "access.log"
    log_file.write_text("")

    source = NginxLogSource(str(log_file))

    try:
        # First call initializes the reader at the end.
        assert source.read_new_records() == []

        with log_file.open("a") as file:
            file.write(make_nginx_line() + "\n")
            file.write(
                make_nginx_line(ip="192.168.1.20") + "\n"
            )

        records = source.read_new_records()

        assert len(records) == 2
        assert records[0].remote_addr == "192.168.1.10"
        assert records[1].remote_addr == "192.168.1.20"

        # No new data should return an empty list.
        assert source.read_new_records() == []

    finally:
        source.close()


def test_log_source_waits_for_incomplete_line(tmp_path):
    log_file = tmp_path / "access.log"
    log_file.write_text("")

    source = NginxLogSource(str(log_file))
    line = make_nginx_line()

    try:
        assert source.read_new_records() == []

        # Append an incomplete line without its newline.
        with log_file.open("a") as file:
            file.write(line)

        assert source.read_new_records() == []

        # Complete the line in the next read.
        with log_file.open("a") as file:
            file.write("\n")

        records = source.read_new_records()

        assert len(records) == 1
        assert records[0].remote_addr == "192.168.1.10"

    finally:
        source.close()


# ---------------------------------------------------------
# 3. FIXED WINDOW AGGREGATOR
# ---------------------------------------------------------

def test_window_aggregator_groups_records_into_ten_second_windows():
    aggregator = FixedWindowAggregator(window_seconds=10)

    start = datetime(2026, 11, 23, 10, 0, 0, tzinfo=UTC)

    records = [
        make_record(start + timedelta(seconds=2)),
        make_record(start + timedelta(seconds=5)),
        make_record(start + timedelta(seconds=12)),
    ]

    aggregator.add(records)

    # At 10:00:10, only the first window is ready.
    ready = aggregator.pop_ready_windows(
        start + timedelta(seconds=10)
    )

    assert len(ready) == 1

    window_start, window_end, window_records = ready[0]

    assert window_start == start
    assert window_end == start + timedelta(seconds=10)
    assert len(window_records) == 2

    # At 10:00:20, the second window is ready.
    ready = aggregator.pop_ready_windows(
        start + timedelta(seconds=20)
    )

    assert len(ready) == 1
    assert len(ready[0][2]) == 1


def test_window_aggregator_removes_popped_windows():
    aggregator = FixedWindowAggregator(window_seconds=10)

    start = datetime(2026, 11, 23, 10, 0, 0, tzinfo=UTC)

    aggregator.add([
        make_record(start + timedelta(seconds=1))
    ])

    ready = aggregator.pop_ready_windows(
        start + timedelta(seconds=10)
    )

    assert len(ready) == 1

    # The same window must not be returned again.
    assert aggregator.pop_ready_windows(
        start + timedelta(seconds=20)
    ) == []


def test_window_aggregator_rejects_invalid_window_size():
    try:
        FixedWindowAggregator(window_seconds=0)
        raise AssertionError("Expected ValueError")
    except ValueError:
        pass


# ---------------------------------------------------------
# 4. WINDOW FEATURE EXTRACTOR
# ---------------------------------------------------------

def test_feature_extractor_calculates_traffic_features():
    extractor = WindowFeatureExtractor()

    start = datetime(2026, 11, 23, 10, 0, 0, tzinfo=UTC)
    end = start + timedelta(seconds=10)

    records = [
        make_record(
            start + timedelta(seconds=1),
            ip="192.168.1.10",
            path="/products",
            status=200,
            latency=20,
        ),
        make_record(
            start + timedelta(seconds=2),
            ip="192.168.1.10",
            path="/products",
            status=404,
            latency=30,
        ),
        make_record(
            start + timedelta(seconds=3),
            ip="192.168.1.20",
            path="/login",
            status=500,
            latency=40,
        ),
    ]

    features = extractor.extract(records, start, end)

    assert features.total_requests == 3
    assert features.duration_s == 10
    assert features.requests_per_sec == 0.3

    assert features.unique_ips == 2
    assert features.top_ip == "192.168.1.10"
    assert features.max_requests_per_ip == 2
    assert features.top_ip_share == 2 / 3

    assert features.top_endpoint == "/products"
    assert features.top_endpoint_share == 2 / 3

    assert features.status_4xx_rate == 1 / 3
    assert features.status_5xx_rate == 1 / 3

    assert features.avg_latency_ms == 30.0
    assert features.p95_latency_ms > 0


def test_feature_extractor_handles_empty_window():
    extractor = WindowFeatureExtractor()

    start = datetime(2026, 11, 23, 10, 0, 0, tzinfo=UTC)
    end = start + timedelta(seconds=10)

    features = extractor.extract([], start, end)

    assert features.total_requests == 0
    assert features.requests_per_sec == 0
    assert features.unique_ips == 0
    assert features.top_ip is None
    assert features.top_endpoint is None
    assert features.avg_latency_ms == 0
    assert features.p95_latency_ms == 0


def test_feature_extractor_rejects_zero_duration():
    extractor = WindowFeatureExtractor()

    now = datetime.now(UTC)

    try:
        extractor.extract([], now, now)
        raise AssertionError("Expected ValueError")
    except ValueError:
        pass


# ---------------------------------------------------------
# 5. IN-MEMORY BASELINE STORE
# ---------------------------------------------------------

def test_baseline_returns_none_before_thirty_samples():
    store = InMemoryBaselineStore()

    at = datetime(2026, 11, 23, 10, 0, tzinfo=UTC)

    assert store.get(at) is None


def test_baseline_builds_profile_after_thirty_samples():
    store = InMemoryBaselineStore()
    extractor = WindowFeatureExtractor()

    start = datetime(2026, 11, 23, 10, 0, tzinfo=UTC)

    for i in range(30):
        window_start = start + timedelta(seconds=i * 10)
        window_end = window_start + timedelta(seconds=10)

        records = [
            make_record(
                window_start + timedelta(seconds=1),
                ip="192.168.1.10",
                latency=20,
            )
        ]

        features = extractor.extract(
            records,
            window_start,
            window_end,
        )

        store.update(features)

    profile = store.get(start)

    assert profile is not None
    assert profile.sample_count == 30
    assert profile.last_updated == start + timedelta(seconds=300)

    assert "10" in profile.requests_per_sec
    assert profile.requests_per_sec["10"].mean == 0.1
    assert profile.requests_per_sec["10"].std == 0.0

    assert "10" in profile.unique_ips
    assert profile.unique_ips["10"].mean == 1.0


def test_baseline_rejects_naive_datetime():
    store = InMemoryBaselineStore()

    try:
        store.get(datetime(2026, 11, 23, 10, 0))
        raise AssertionError("Expected ValueError")
    except ValueError:
        pass
