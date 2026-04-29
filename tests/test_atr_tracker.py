"""Tests for ATR tracker."""
from __future__ import annotations

import pytest
from alpaca_stream_cli.atr_tracker import ATRTracker, SymbolATR, _true_range


# ---------------------------------------------------------------------------
# _true_range helpers
# ---------------------------------------------------------------------------

def test_true_range_no_prev_close():
    assert _true_range(110, 100, None) == pytest.approx(10.0)


def test_true_range_prev_close_above_high():
    # prev_close=120 > high=110 => hc=10, lc=20, hl=10 => 20
    assert _true_range(110, 100, 120) == pytest.approx(20.0)


def test_true_range_prev_close_below_low():
    # prev_close=90 < low=100 => lc=10, hc=20, hl=10 => 20
    assert _true_range(110, 100, 90) == pytest.approx(20.0)


def test_true_range_prev_close_within_range():
    assert _true_range(110, 100, 105) == pytest.approx(10.0)


# ---------------------------------------------------------------------------
# SymbolATR
# ---------------------------------------------------------------------------

def test_invalid_period_raises():
    with pytest.raises(ValueError):
        SymbolATR(period=0)


def test_no_value_before_period_filled():
    sa = SymbolATR(period=3)
    sa.record(110, 100, 105)
    sa.record(112, 102, 108)
    assert sa.value is None


def test_value_after_period_filled():
    sa = SymbolATR(period=3)
    sa.record(110, 100, 105)
    sa.record(112, 102, 108)
    result = sa.record(115, 105, 110)
    assert result is not None
    assert sa.value is not None
    assert sa.value > 0


def test_high_less_than_low_raises():
    sa = SymbolATR(period=3)
    with pytest.raises(ValueError):
        sa.record(90, 100, 95)


def test_negative_close_raises():
    sa = SymbolATR(period=3)
    with pytest.raises(ValueError):
        sa.record(110, 100, -1)


def test_trade_count_increments():
    sa = SymbolATR(period=3)
    sa.record(110, 100, 105)
    sa.record(112, 102, 108)
    assert sa.trade_count == 2


# ---------------------------------------------------------------------------
# ATRTracker
# ---------------------------------------------------------------------------

@pytest.fixture
def tracker():
    return ATRTracker(period=3, max_symbols=10)


def test_invalid_max_symbols_raises():
    with pytest.raises(ValueError):
        ATRTracker(max_symbols=0)


def test_invalid_period_on_tracker_raises():
    with pytest.raises(ValueError):
        ATRTracker(period=0)


def test_record_normalizes_symbol_to_uppercase(tracker):
    tracker.record("aapl", 150, 145, 148)
    assert "AAPL" in tracker.symbols()


def test_no_result_before_period_filled(tracker):
    result = tracker.record("AAPL", 150, 145, 148)
    assert result is None


def test_result_after_period_filled(tracker):
    tracker.record("AAPL", 150, 145, 148)
    tracker.record("AAPL", 152, 147, 150)
    result = tracker.record("AAPL", 155, 149, 153)
    assert result is not None
    assert result.symbol == "AAPL"
    assert result.atr > 0


def test_result_symbol_is_uppercase(tracker):
    tracker.record("msft", 300, 295, 298)
    tracker.record("msft", 302, 297, 300)
    result = tracker.record("msft", 305, 299, 303)
    assert result is not None
    assert result.symbol == "MSFT"


def test_get_returns_none_for_unknown_symbol(tracker):
    assert tracker.get("UNKNOWN") is None


def test_max_symbols_not_exceeded(tracker):
    for i in range(10):
        tracker.record(f"SYM{i}", 100, 95, 98)
    result = tracker.record("EXTRA", 100, 95, 98)
    assert result is None
    assert "EXTRA" not in tracker.symbols()
