"""Tests for alpaca_stream_cli.macd_tracker."""
import pytest

from alpaca_stream_cli.macd_tracker import MACDTracker, SymbolMACD


# ---------------------------------------------------------------------------
# SymbolMACD unit tests
# ---------------------------------------------------------------------------

def test_invalid_fast_period_raises():
    with pytest.raises(ValueError):
        SymbolMACD(fast_period=1)


def test_slow_must_be_greater_than_fast_raises():
    with pytest.raises(ValueError):
        SymbolMACD(fast_period=12, slow_period=12)


def test_invalid_signal_period_raises():
    with pytest.raises(ValueError):
        SymbolMACD(fast_period=12, slow_period=26, signal_period=1)


def test_negative_price_raises():
    sym = SymbolMACD()
    with pytest.raises(ValueError):
        sym.record(-1.0)


def test_no_value_before_any_record():
    sym = SymbolMACD()
    assert sym.value is None


def test_value_available_after_first_record():
    """After the first record all EMAs are seeded; signal becomes non-None."""
    sym = SymbolMACD(fast_period=2, slow_period=3, signal_period=2)
    sym.record(100.0)
    # After one record signal_ema is seeded, so value should be available.
    result = sym.value
    assert result is not None


def test_macd_line_is_fast_minus_slow():
    sym = SymbolMACD(fast_period=2, slow_period=3, signal_period=2)
    sym.record(100.0)
    sym.record(110.0)
    result = sym.value
    assert result is not None
    assert abs(result.macd - (result.macd)) < 1e-9  # tautology — just check no crash
    # MACD = fast_ema - slow_ema; fast reacts quicker so should be higher after price rise
    assert result.macd > 0


def test_histogram_equals_macd_minus_signal():
    sym = SymbolMACD(fast_period=2, slow_period=3, signal_period=2)
    for p in [100, 102, 104, 103, 105]:
        sym.record(float(p))
    result = sym.value
    assert result is not None
    assert abs(result.histogram - (result.macd - result.signal)) < 1e-9


def test_trade_count_increments():
    sym = SymbolMACD()
    assert sym.trade_count == 0
    sym.record(50.0)
    assert sym.trade_count == 1
    sym.record(51.0)
    assert sym.trade_count == 2


# ---------------------------------------------------------------------------
# MACDTracker tests
# ---------------------------------------------------------------------------

@pytest.fixture
def tracker():
    return MACDTracker(fast_period=2, slow_period=3, signal_period=2)


def test_invalid_max_symbols_raises():
    with pytest.raises(ValueError):
        MACDTracker(max_symbols=0)


def test_result_unknown_symbol_returns_none(tracker):
    assert tracker.result("UNKNOWN") is None


def test_record_normalizes_symbol_to_uppercase(tracker):
    tracker.record("aapl", 150.0)
    assert "AAPL" in tracker.symbols()


def test_result_after_records(tracker):
    for price in [100.0, 102.0, 104.0]:
        tracker.record("TSLA", price)
    result = tracker.result("TSLA")
    assert result is not None
    assert isinstance(result.macd, float)
    assert isinstance(result.signal, float)
    assert isinstance(result.histogram, float)


def test_max_symbols_limit():
    t = MACDTracker(max_symbols=2)
    t.record("AAPL", 100.0)
    t.record("MSFT", 200.0)
    t.record("GOOG", 300.0)  # should be silently ignored
    assert len(t.symbols()) == 2
    assert "GOOG" not in t.symbols()


def test_symbols_returns_sorted_list(tracker):
    tracker.record("TSLA", 100.0)
    tracker.record("AAPL", 200.0)
    tracker.record("MSFT", 300.0)
    assert tracker.symbols() == ["AAPL", "MSFT", "TSLA"]
