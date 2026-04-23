"""Tests for alpaca_stream_cli.price_change_tracker."""
from datetime import datetime, timezone

import pytest

from alpaca_stream_cli.price_change_tracker import PriceChangeTracker, SymbolVelocity


def _ts(offset_seconds: float = 0.0) -> datetime:
    """Return a fixed UTC datetime optionally offset by *offset_seconds*."""
    base = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    from datetime import timedelta
    return base + timedelta(seconds=offset_seconds)


@pytest.fixture()
def tracker() -> PriceChangeTracker:
    return PriceChangeTracker()


def test_invalid_max_ticks_raises():
    with pytest.raises(ValueError):
        PriceChangeTracker(max_ticks_per_symbol=0)


def test_record_normalizes_symbol_to_uppercase(tracker):
    tracker.record("aapl", 150.0, _ts())
    assert tracker.get("AAPL") is not None
    assert tracker.get("aapl") is not None


def test_latest_price_after_single_record(tracker):
    tracker.record("AAPL", 150.0, _ts())
    sv = tracker.get("AAPL")
    assert sv is not None
    assert sv.latest_price == 150.0


def test_latest_price_is_most_recent(tracker):
    tracker.record("AAPL", 150.0, _ts(0))
    tracker.record("AAPL", 152.5, _ts(5))
    assert tracker.get("AAPL").latest_price == 152.5


def test_change_over_window_returns_none_for_single_tick(tracker):
    tracker.record("MSFT", 300.0, _ts())
    assert tracker.get("MSFT").change_over_window(60) is None


def test_change_over_window_correct_value(tracker):
    tracker.record("MSFT", 300.0, _ts(0))
    tracker.record("MSFT", 303.0, _ts(30))
    result = tracker.get("MSFT").change_over_window(60)
    assert result == pytest.approx(3.0)


def test_change_over_window_excludes_old_ticks(tracker):
    tracker.record("TSLA", 200.0, _ts(0))   # outside 30-s window
    tracker.record("TSLA", 205.0, _ts(70))
    tracker.record("TSLA", 208.0, _ts(90))
    # window=30s from latest (t=90): includes t=70 and t=90
    result = tracker.get("TSLA").change_over_window(30)
    assert result == pytest.approx(3.0)


def test_pct_change_over_window_correct(tracker):
    tracker.record("GOOG", 100.0, _ts(0))
    tracker.record("GOOG", 110.0, _ts(10))
    pct = tracker.get("GOOG").pct_change_over_window(60)
    assert pct == pytest.approx(10.0)


def test_pct_change_returns_none_when_base_is_zero(tracker):
    tracker.record("ZZZ", 0.0, _ts(0))
    tracker.record("ZZZ", 1.0, _ts(5))
    assert tracker.get("ZZZ").pct_change_over_window(60) is None


def test_symbols_returns_sorted_list(tracker):
    tracker.record("TSLA", 1.0, _ts())
    tracker.record("AAPL", 1.0, _ts())
    tracker.record("MSFT", 1.0, _ts())
    assert tracker.symbols() == ["AAPL", "MSFT", "TSLA"]


def test_remove_existing_symbol(tracker):
    tracker.record("AAPL", 150.0, _ts())
    assert tracker.remove("AAPL") is True
    assert tracker.get("AAPL") is None


def test_remove_nonexistent_symbol_returns_false(tracker):
    assert tracker.remove("FAKE") is False


def test_get_unknown_symbol_returns_none(tracker):
    assert tracker.get("UNKNOWN") is None


def test_max_ticks_respected():
    t = PriceChangeTracker(max_ticks_per_symbol=3)
    for i in range(5):
        t.record("AAPL", float(100 + i), _ts(i))
    sv = t.get("AAPL")
    assert len(sv._ticks) == 3
    assert sv.latest_price == 104.0
