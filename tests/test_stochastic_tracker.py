"""Tests for StochasticTracker and SymbolStochastic."""
import pytest
from alpaca_stream_cli.stochastic_tracker import (
    StochasticResult,
    StochasticTracker,
    SymbolStochastic,
)


# --- SymbolStochastic unit tests ---

def test_invalid_k_period_raises():
    with pytest.raises(ValueError, match="k_period"):
        SymbolStochastic(k_period=1)


def test_invalid_d_period_raises():
    with pytest.raises(ValueError, match="d_period"):
        SymbolStochastic(d_period=0)


def test_negative_price_raises():
    s = SymbolStochastic()
    with pytest.raises(ValueError, match="non-negative"):
        s.record(-1.0)


def test_no_value_before_k_period_filled():
    s = SymbolStochastic(k_period=3, d_period=2)
    s.record(10.0)
    s.record(11.0)
    assert s.value is None


def test_no_value_before_d_period_filled():
    s = SymbolStochastic(k_period=3, d_period=3)
    for p in [10.0, 11.0, 12.0, 13.0]:  # fills k_period, but only 2 k values
        s.record(p)
    assert s.value is None


def test_value_after_periods_filled():
    s = SymbolStochastic(k_period=3, d_period=2)
    prices = [10.0, 11.0, 12.0, 11.5]
    for p in prices:
        s.record(p)
    result = s.value
    assert result is not None
    assert isinstance(result.k, float)
    assert isinstance(result.d, float)
    assert 0.0 <= result.k <= 100.0


def test_k_equals_100_at_highest_price():
    s = SymbolStochastic(k_period=3, d_period=1)
    s.record(10.0)
    s.record(11.0)
    s.record(12.0)  # highest in window
    result = s.value
    assert result is not None
    assert result.k == pytest.approx(100.0)


def test_k_equals_0_at_lowest_price():
    s = SymbolStochastic(k_period=3, d_period=1)
    s.record(12.0)
    s.record(11.0)
    s.record(10.0)  # lowest in window
    result = s.value
    assert result is not None
    assert result.k == pytest.approx(0.0)


def test_k_equals_50_when_high_equals_low():
    s = SymbolStochastic(k_period=3, d_period=1)
    for _ in range(3):
        s.record(10.0)
    result = s.value
    assert result is not None
    assert result.k == pytest.approx(50.0)


def test_overbought_flag():
    r = StochasticResult(k=85.0, d=80.0)
    assert r.is_overbought is True
    assert r.is_oversold is False


def test_oversold_flag():
    r = StochasticResult(k=15.0, d=20.0)
    assert r.is_oversold is True
    assert r.is_overbought is False


def test_sample_count_tracks_records():
    s = SymbolStochastic(k_period=5, d_period=2)
    for i in range(4):
        s.record(float(i + 10))
    assert s.sample_count == 4


# --- StochasticTracker integration tests ---

def test_invalid_max_symbols_raises():
    with pytest.raises(ValueError, match="max_symbols"):
        StochasticTracker(max_symbols=0)


def test_record_normalizes_symbol_to_uppercase():
    t = StochasticTracker(k_period=3, d_period=1)
    prices = [10.0, 11.0, 12.0]
    for p in prices:
        t.record("aapl", p)
    assert "AAPL" in t.symbols


def test_result_none_for_unknown_symbol():
    t = StochasticTracker()
    assert t.result("UNKNOWN") is None


def test_result_available_after_enough_records():
    t = StochasticTracker(k_period=3, d_period=1)
    for p in [10.0, 11.0, 12.0]:
        t.record("MSFT", p)
    result = t.result("MSFT")
    assert result is not None
    assert result.k == pytest.approx(100.0)


def test_multiple_symbols_tracked_independently():
    t = StochasticTracker(k_period=3, d_period=1)
    for p in [10.0, 11.0, 12.0]:
        t.record("AAPL", p)
    for p in [20.0, 19.0, 18.0]:
        t.record("GOOG", p)
    r_aapl = t.result("AAPL")
    r_goog = t.result("GOOG")
    assert r_aapl is not None
    assert r_goog is not None
    assert r_aapl.k == pytest.approx(100.0)
    assert r_goog.k == pytest.approx(0.0)
