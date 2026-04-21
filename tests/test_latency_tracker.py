"""Tests for alpaca_stream_cli.latency_tracker."""

from datetime import datetime, timedelta, timezone

import pytest

from alpaca_stream_cli.latency_tracker import LatencyTracker, SymbolLatency


@pytest.fixture()
def tracker() -> LatencyTracker:
    return LatencyTracker()


def _ts(offset_ms: float = 0.0) -> datetime:
    """Return a UTC datetime slightly in the past to simulate exchange timestamp."""
    return datetime.now(tz=timezone.utc) - timedelta(milliseconds=offset_ms)


def test_invalid_max_symbols_raises() -> None:
    with pytest.raises(ValueError):
        LatencyTracker(max_symbols=0)


def test_record_returns_positive_latency(tracker: LatencyTracker) -> None:
    latency = tracker.record("AAPL", _ts(offset_ms=10))
    assert latency >= 0


def test_record_normalizes_symbol_to_uppercase(tracker: LatencyTracker) -> None:
    tracker.record("aapl", _ts(10))
    assert tracker.get("AAPL") is not None
    assert tracker.get("aapl") is not None


def test_get_unknown_symbol_returns_none(tracker: LatencyTracker) -> None:
    assert tracker.get("UNKNOWN") is None


def test_average_ms_after_multiple_records(tracker: LatencyTracker) -> None:
    for _ in range(5):
        tracker.record("TSLA", _ts(20))
    sl = tracker.get("TSLA")
    assert sl is not None
    assert sl.average_ms is not None
    assert sl.average_ms >= 0


def test_min_max_last_populated(tracker: LatencyTracker) -> None:
    tracker.record("MSFT", _ts(5))
    tracker.record("MSFT", _ts(15))
    sl = tracker.get("MSFT")
    assert sl.min_ms is not None
    assert sl.max_ms is not None
    assert sl.last_ms is not None
    assert sl.min_ms <= sl.max_ms


def test_symbol_latency_max_samples_respected() -> None:
    sl = SymbolLatency()
    for i in range(60):
        sl.record(float(i))
    assert len(sl.samples) == 50


def test_symbols_list(tracker: LatencyTracker) -> None:
    tracker.record("AAPL", _ts(10))
    tracker.record("GOOG", _ts(10))
    syms = tracker.symbols()
    assert "AAPL" in syms
    assert "GOOG" in syms


def test_reset_removes_symbol(tracker: LatencyTracker) -> None:
    tracker.record("AAPL", _ts(10))
    tracker.reset("AAPL")
    assert tracker.get("AAPL") is None


def test_clear_removes_all(tracker: LatencyTracker) -> None:
    tracker.record("AAPL", _ts(10))
    tracker.record("TSLA", _ts(10))
    tracker.clear()
    assert tracker.symbols() == []


def test_max_symbols_evicts_oldest(tracker: LatencyTracker) -> None:
    small = LatencyTracker(max_symbols=3)
    small.record("A", _ts(5))
    small.record("B", _ts(5))
    small.record("C", _ts(5))
    small.record("D", _ts(5))
    assert len(small.symbols()) == 3
    assert "A" not in small.symbols()
