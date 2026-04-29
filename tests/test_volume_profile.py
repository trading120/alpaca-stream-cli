"""Tests for VolumeProfileTracker and VolumeProfileResult."""
from __future__ import annotations

import pytest

from alpaca_stream_cli.volume_profile import (
    VolumeProfileTracker,
    VolumeProfileResult,
)


@pytest.fixture()
def tracker() -> VolumeProfileTracker:
    return VolumeProfileTracker(tick_size=0.01)


def test_invalid_tick_size_raises():
    with pytest.raises(ValueError):
        VolumeProfileTracker(tick_size=0)


def test_invalid_max_symbols_raises():
    with pytest.raises(ValueError):
        VolumeProfileTracker(tick_size=0.01, max_symbols=0)


def test_record_returns_result(tracker):
    result = tracker.record("AAPL", 150.00, 100)
    assert isinstance(result, VolumeProfileResult)
    assert result.symbol == "AAPL"


def test_record_normalizes_symbol_to_uppercase(tracker):
    result = tracker.record("aapl", 150.00, 50)
    assert result.symbol == "AAPL"


def test_poc_is_highest_volume_price(tracker):
    tracker.record("TSLA", 200.00, 500)
    tracker.record("TSLA", 200.50, 1500)
    tracker.record("TSLA", 201.00, 300)
    result = tracker.get("TSLA")
    assert result is not None
    assert result.poc == pytest.approx(200.50, abs=0.001)


def test_total_volume_accumulates(tracker):
    tracker.record("MSFT", 300.00, 100)
    tracker.record("MSFT", 300.00, 200)
    tracker.record("MSFT", 301.00, 50)
    result = tracker.get("MSFT")
    assert result.total_volume == pytest.approx(350.0)


def test_same_price_accumulates_in_same_bucket(tracker):
    tracker.record("GOOG", 140.00, 100)
    tracker.record("GOOG", 140.005, 200)  # rounds to same 0.01 bucket
    result = tracker.get("GOOG")
    assert len(result.levels) == 1
    assert result.total_volume == pytest.approx(300.0)


def test_value_area_covers_pct_of_volume(tracker):
    tracker.record("NVDA", 500.00, 1000)
    tracker.record("NVDA", 501.00, 500)
    tracker.record("NVDA", 502.00, 300)
    tracker.record("NVDA", 503.00, 200)
    result = tracker.get("NVDA")
    va_low, va_high = result.value_area(0.70)
    assert va_low <= va_high


def test_value_area_empty_returns_zeros():
    result = VolumeProfileResult(symbol="X", levels={}, poc=None, total_volume=0.0)
    assert result.value_area() == (0.0, 0.0)


def test_get_before_any_data_returns_none(tracker):
    assert tracker.get("SPY") is None


def test_reset_clears_symbol(tracker):
    tracker.record("AMD", 100.00, 200)
    tracker.reset("AMD")
    assert tracker.get("AMD") is None


def test_reset_all_clears_everything(tracker):
    tracker.record("A", 10.0, 100)
    tracker.record("B", 20.0, 200)
    tracker.reset_all()
    assert tracker.symbols == []


def test_max_symbols_overflow_raises(tracker):
    t = VolumeProfileTracker(tick_size=0.01, max_symbols=2)
    t.record("A", 10.0, 1)
    t.record("B", 20.0, 1)
    with pytest.raises(OverflowError):
        t.record("C", 30.0, 1)


def test_negative_price_raises(tracker):
    with pytest.raises(ValueError):
        tracker.record("X", -1.0, 100)


def test_negative_volume_raises(tracker):
    with pytest.raises(ValueError):
        tracker.record("X", 10.0, -1)


def test_symbols_property(tracker):
    tracker.record("AAPL", 150.0, 100)
    tracker.record("MSFT", 300.0, 200)
    assert set(tracker.symbols) == {"AAPL", "MSFT"}
