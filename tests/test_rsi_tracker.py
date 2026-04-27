"""Tests for alpaca_stream_cli.rsi_tracker."""
import pytest

from alpaca_stream_cli.rsi_tracker import RSITracker, SymbolRSI


# ---------------------------------------------------------------------------
# SymbolRSI unit tests
# ---------------------------------------------------------------------------

def test_invalid_period_raises():
    with pytest.raises(ValueError, match="period"):
        SymbolRSI(period=1)


def test_no_value_before_period_filled():
    rsi = SymbolRSI(period=3)
    rsi.record(10.0)
    rsi.record(11.0)
    assert rsi.value is None


def test_value_after_period_filled():
    rsi = SymbolRSI(period=3)
    for price in [10.0, 11.0, 12.0, 11.5]:
        rsi.record(price)
    assert rsi.value is not None
    assert 0.0 <= rsi.value <= 100.0


def test_all_gains_gives_rsi_100():
    rsi = SymbolRSI(period=3)
    for price in [10.0, 11.0, 12.0, 13.0, 14.0]:
        rsi.record(price)
    assert rsi.value == pytest.approx(100.0)


def test_all_losses_gives_rsi_near_zero():
    rsi = SymbolRSI(period=3)
    for price in [14.0, 13.0, 12.0, 11.0, 10.0]:
        rsi.record(price)
    assert rsi.value == pytest.approx(0.0, abs=1e-6)


def test_negative_price_raises():
    rsi = SymbolRSI(period=3)
    with pytest.raises(ValueError, match="non-negative"):
        rsi.record(-1.0)


def test_trade_count_increments():
    rsi = SymbolRSI(period=3)
    rsi.record(10.0)  # sets prev_price, no count
    rsi.record(11.0)
    rsi.record(12.0)
    assert rsi.trade_count == 2


def test_rsi_value_in_range_for_mixed_moves():
    rsi = SymbolRSI(period=5)
    prices = [44, 46, 45, 47, 43, 48, 44, 46, 45, 47]
    for p in prices:
        rsi.record(float(p))
    val = rsi.value
    assert val is not None
    assert 0.0 < val < 100.0


# ---------------------------------------------------------------------------
# RSITracker integration tests
# ---------------------------------------------------------------------------

@pytest.fixture
def tracker():
    return RSITracker(period=3)


def test_invalid_tracker_period_raises():
    with pytest.raises(ValueError, match="period"):
        RSITracker(period=1)


def test_invalid_max_symbols_raises():
    with pytest.raises(ValueError, match="max_symbols"):
        RSITracker(max_symbols=0)


def test_tracker_value_none_before_period(tracker):
    tracker.record("AAPL", 150.0)
    tracker.record("AAPL", 151.0)
    assert tracker.value("AAPL") is None


def test_tracker_value_after_period(tracker):
    for p in [150.0, 151.0, 152.0, 151.5]:
        tracker.record("AAPL", p)
    assert tracker.value("AAPL") is not None


def test_tracker_normalizes_symbol_case(tracker):
    for p in [10.0, 11.0, 12.0, 13.0]:
        tracker.record("aapl", p)
    assert tracker.value("AAPL") is not None
    assert "AAPL" in tracker.symbols()


def test_tracker_unknown_symbol_returns_none(tracker):
    assert tracker.value("TSLA") is None


def test_tracker_reset_clears_symbol(tracker):
    for p in [10.0, 11.0, 12.0, 13.0]:
        tracker.record("MSFT", p)
    tracker.reset("MSFT")
    assert tracker.value("MSFT") is None
    assert "MSFT" not in tracker.symbols()


def test_tracker_max_symbols_respected():
    t = RSITracker(period=3, max_symbols=2)
    t.record("A", 1.0)
    t.record("B", 2.0)
    t.record("C", 3.0)  # should be silently ignored
    assert "C" not in t.symbols()
    assert len(t.symbols()) == 2
