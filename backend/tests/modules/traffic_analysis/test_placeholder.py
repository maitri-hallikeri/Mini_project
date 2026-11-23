"""
Placeholder tests for the traffic_analysis module.

Owner: Member 1.
"""

from __future__ import annotations

from datetime import UTC

import pytest


@pytest.mark.skip(reason="TODO(member1): add module tests")
def test_traffic_analysis_placeholder():
    """Placeholder — Member 1 must replace this with real tests."""


def test_nginx_log_source_raises_not_implemented():
    """NginxLogSource.read_new_records() must raise NotImplementedError."""
    from app.modules.traffic_analysis.log_source import NginxLogSource

    source = NginxLogSource("/var/log/nginx/access.log")
    with pytest.raises(NotImplementedError):
        source.read_new_records()


def test_nginx_log_parser_raises_not_implemented():
    """NginxLogParser.parse_line() must raise NotImplementedError."""
    from app.modules.traffic_analysis.parser import NginxLogParser

    parser = NginxLogParser()
    with pytest.raises(NotImplementedError):
        parser.parse_line("127.0.0.1 - - [01/Jan/2026:00:00:00 +0000] ...")


def test_window_aggregator_add_raises_not_implemented():
    """FixedWindowAggregator.add() must raise NotImplementedError."""
    from app.modules.traffic_analysis.windowing import FixedWindowAggregator

    agg = FixedWindowAggregator()
    with pytest.raises(NotImplementedError):
        agg.add([])


def test_feature_extractor_raises_not_implemented():
    """WindowFeatureExtractor.extract() must raise NotImplementedError."""
    from datetime import datetime

    from app.modules.traffic_analysis.features import WindowFeatureExtractor

    extractor = WindowFeatureExtractor()
    now = datetime.now(UTC)
    with pytest.raises(NotImplementedError):
        extractor.extract([], now, now)


def test_baseline_store_get_raises_not_implemented():
    """InMemoryBaselineStore.get() must raise NotImplementedError."""
    from datetime import datetime

    from app.modules.traffic_analysis.baseline import InMemoryBaselineStore

    store = InMemoryBaselineStore()
    with pytest.raises(NotImplementedError):
        store.get(datetime.now(UTC))
