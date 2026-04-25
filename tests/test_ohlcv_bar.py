"""Tests for OHLCVBar and OHLCVTracker."""
from datetime import datetime, timezone
import pytest

from alpaca_stream_cli.ohlcv_bar import OHLCVBar, OHLCVTracker


@pytest.fixture
def tracker() -> OHLCVTracker:
    return OHLCVTracker(max_symbols=10)


def _ts(offset: int = 0) -> datetime:
    return datetime(2024, 1, 1, 9, 30, offset, tzinfo=timezone.utc)


def test_invalid_max_symbols_raises():
    with pytest.raises(ValueError):
        OHLCVTracker(max_symbols=0)


def test_first_record_sets_ohlc(tracker):
    bar = tracker.record("AAPL", 150.0, 100, _ts(0))
    assert bar.open == 150.0
    assert bar.high == 150.0
    assert bar.low == 150.0
    assert bar.close == 150.0
    assert bar.volume == 100


def test_record_normalizes_symbol_to_uppercase(tracker):
    bar = tracker.record("aapl", 100.0, 50, _ts(0))
    assert bar.symbol == "AAPL"


def test_high_updated_on_higher_price(tracker):
    tracker.record("TSLA", 200.0, 10, _ts(0))
    bar = tracker.record("TSLA", 210.0, 10, _ts(1))
    assert bar.high == 210.0
    assert bar.open == 200.0


def test_low_updated_on_lower_price(tracker):
    tracker.record("TSLA", 200.0, 10, _ts(0))
    bar = tracker.record("TSLA", 190.0, 10, _ts(1))
    assert bar.low == 190.0


def test_close_follows_latest_price(tracker):
    tracker.record("MSFT", 300.0, 5, _ts(0))
    bar = tracker.record("MSFT", 305.0, 5, _ts(1))
    assert bar.close == 305.0


def test_volume_accumulates(tracker):
    tracker.record("NVDA", 400.0, 100, _ts(0))
    bar = tracker.record("NVDA", 402.0, 200, _ts(1))
    assert bar.volume == 300


def test_change_and_change_pct(tracker):
    tracker.record("GOOG", 100.0, 1, _ts(0))
    bar = tracker.record("GOOG", 110.0, 1, _ts(1))
    assert bar.change == pytest.approx(10.0)
    assert bar.change_pct == pytest.approx(10.0)


def test_range_property(tracker):
    tracker.record("AMD", 80.0, 1, _ts(0))
    tracker.record("AMD", 90.0, 1, _ts(1))
    bar = tracker.record("AMD", 75.0, 1, _ts(2))
    assert bar.range == pytest.approx(15.0)


def test_get_returns_snapshot(tracker):
    tracker.record("AAPL", 150.0, 100, _ts(0))
    bar = tracker.get("aapl")
    assert bar is not None
    assert bar.symbol == "AAPL"


def test_get_unknown_returns_none(tracker):
    assert tracker.get("UNKNOWN") is None


def test_reset_removes_symbol(tracker):
    tracker.record("AAPL", 150.0, 100, _ts(0))
    tracker.reset("AAPL")
    assert tracker.get("AAPL") is None


def test_max_symbols_evicts_oldest(tracker):
    t = OHLCVTracker(max_symbols=2)
    t.record("A", 1.0, 1, _ts(0))
    t.record("B", 2.0, 1, _ts(1))
    t.record("C", 3.0, 1, _ts(2))
    assert t.get("A") is None
    assert t.get("B") is not None
    assert t.get("C") is not None


def test_symbols_returns_tracked_list(tracker):
    tracker.record("AAPL", 1.0, 1, _ts(0))
    tracker.record("MSFT", 2.0, 1, _ts(1))
    assert set(tracker.symbols()) == {"AAPL", "MSFT"}
