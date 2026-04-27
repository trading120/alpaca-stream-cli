"""Tests for BollingerTracker and BollingerResult."""
import math
import pytest

from alpaca_stream_cli.bollinger_bands import (
    BollingerResult,
    BollingerTracker,
    SymbolBollinger,
)


# --- SymbolBollinger ---

def test_invalid_period_raises():
    with pytest.raises(ValueError, match="period"):
        SymbolBollinger(period=1)


def test_invalid_num_std_raises():
    with pytest.raises(ValueError, match="num_std"):
        SymbolBollinger(num_std=0.0)


def test_negative_price_raises():
    sb = SymbolBollinger(period=3)
    with pytest.raises(ValueError, match="price"):
        sb.record(-1.0)


def test_no_result_before_period_filled():
    sb = SymbolBollinger(period=5)
    for p in [10.0, 11.0, 12.0, 11.5]:
        sb.record(p)
    assert sb.result("AAPL") is None


def test_result_after_period_filled():
    sb = SymbolBollinger(period=3)
    for p in [10.0, 12.0, 14.0]:
        sb.record(p)
    result = sb.result("AAPL")
    assert result is not None
    assert result.symbol == "AAPL"
    assert math.isclose(result.middle, 12.0, rel_tol=1e-9)


def test_upper_greater_than_middle_greater_than_lower():
    sb = SymbolBollinger(period=4)
    for p in [10.0, 11.0, 13.0, 12.0]:
        sb.record(p)
    r = sb.result("TSLA")
    assert r.upper > r.middle > r.lower


def test_sample_count():
    sb = SymbolBollinger(period=5)
    assert sb.sample_count == 0
    sb.record(10.0)
    assert sb.sample_count == 1


def test_window_rolls_correctly():
    sb = SymbolBollinger(period=3)
    for p in [10.0, 10.0, 10.0]:
        sb.record(p)
    r1 = sb.result("X")
    assert math.isclose(r1.bandwidth, 0.0, abs_tol=1e-9)
    sb.record(20.0)  # now window is [10, 10, 20]
    r2 = sb.result("X")
    assert r2.bandwidth > 0.0


def test_percent_b_above_band():
    r = BollingerResult("A", upper=110.0, middle=100.0, lower=90.0, bandwidth=0.2, price=115.0)
    assert r.percent_b > 1.0


def test_percent_b_below_band():
    r = BollingerResult("A", upper=110.0, middle=100.0, lower=90.0, bandwidth=0.2, price=85.0)
    assert r.percent_b < 0.0


def test_percent_b_middle_is_half():
    r = BollingerResult("A", upper=110.0, middle=100.0, lower=90.0, bandwidth=0.2, price=100.0)
    assert math.isclose(r.percent_b, 0.5, rel_tol=1e-9)


# --- BollingerTracker ---

@pytest.fixture
def tracker():
    return BollingerTracker(period=3, num_std=2.0)


def test_invalid_max_symbols_raises():
    with pytest.raises(ValueError, match="max_symbols"):
        BollingerTracker(max_symbols=0)


def test_record_normalizes_symbol_to_uppercase(tracker):
    for p in [10.0, 11.0, 12.0]:
        tracker.record("aapl", p)
    assert "AAPL" in tracker.tracked_symbols


def test_get_returns_none_for_unknown(tracker):
    assert tracker.get("UNKNOWN") is None


def test_get_returns_none_before_period_filled(tracker):
    tracker.record("MSFT", 100.0)
    assert tracker.get("MSFT") is None


def test_get_returns_result_after_period(tracker):
    for p in [100.0, 102.0, 104.0]:
        tracker.record("MSFT", p)
    r = tracker.get("MSFT")
    assert r is not None
    assert r.symbol == "MSFT"


def test_record_returns_result_when_ready(tracker):
    tracker.record("GOOG", 50.0)
    tracker.record("GOOG", 55.0)
    result = tracker.record("GOOG", 60.0)
    assert result is not None
    assert math.isclose(result.middle, 55.0, rel_tol=1e-9)


def test_multiple_symbols_tracked_independently(tracker):
    for p in [10.0, 11.0, 12.0]:
        tracker.record("A", p)
    for p in [20.0, 21.0]:
        tracker.record("B", p)
    assert tracker.get("A") is not None
    assert tracker.get("B") is None
