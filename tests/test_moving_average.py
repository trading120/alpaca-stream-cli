"""Tests for MovingAverageTracker and SymbolMA."""
import pytest
from alpaca_stream_cli.moving_average import MovingAverageTracker, SymbolMA


# --- SymbolMA unit tests ---

def test_symbol_ma_no_value_before_period_filled():
    ma = SymbolMA(period=3)
    ma.record(10.0)
    ma.record(20.0)
    assert ma.value() is None


def test_symbol_ma_value_when_period_filled():
    ma = SymbolMA(period=3)
    for p in [10.0, 20.0, 30.0]:
        ma.record(p)
    assert ma.value() == pytest.approx(20.0)


def test_symbol_ma_rolls_window():
    ma = SymbolMA(period=3)
    for p in [10.0, 20.0, 30.0, 40.0]:
        ma.record(p)
    # window should be [20, 30, 40]
    assert ma.value() == pytest.approx(30.0)


def test_symbol_ma_negative_price_raises():
    ma = SymbolMA(period=2)
    with pytest.raises(ValueError):
        ma.record(-1.0)


def test_symbol_ma_sample_count():
    ma = SymbolMA(period=5)
    ma.record(1.0)
    ma.record(2.0)
    assert ma.sample_count() == 2


# --- MovingAverageTracker tests ---

@pytest.fixture
def tracker():
    return MovingAverageTracker(short_period=3, long_period=5)


def test_invalid_short_period_raises():
    with pytest.raises(ValueError):
        MovingAverageTracker(short_period=0)


def test_long_period_less_than_short_raises():
    with pytest.raises(ValueError):
        MovingAverageTracker(short_period=5, long_period=3)


def test_invalid_max_symbols_raises():
    with pytest.raises(ValueError):
        MovingAverageTracker(max_symbols=0)


def test_record_normalizes_symbol_to_uppercase(tracker):
    tracker.record("aapl", 150.0)
    assert "AAPL" in tracker.symbols()


def test_short_ma_none_before_period(tracker):
    tracker.record("AAPL", 100.0)
    assert tracker.short_ma("AAPL") is None


def test_short_ma_value_after_period(tracker):
    for p in [100.0, 110.0, 120.0]:
        tracker.record("AAPL", p)
    assert tracker.short_ma("AAPL") == pytest.approx(110.0)


def test_long_ma_none_before_period(tracker):
    for p in [100.0, 110.0, 120.0]:
        tracker.record("AAPL", p)
    assert tracker.long_ma("AAPL") is None


def test_crossover_none_when_insufficient_data(tracker):
    tracker.record("MSFT", 200.0)
    assert tracker.crossover("MSFT") is None


def test_crossover_true_when_short_above_long(tracker):
    # Feed rising prices so short MA > long MA
    prices = [100, 102, 104, 106, 108, 110, 112]
    for p in prices:
        tracker.record("TSLA", float(p))
    result = tracker.crossover("TSLA")
    assert result is True


def test_crossover_false_when_short_below_long():
    t = MovingAverageTracker(short_period=3, long_period=5)
    # Feed falling prices so short MA < long MA
    prices = [110, 108, 106, 104, 102, 100, 98]
    for p in prices:
        t.record("SPY", float(p))
    assert t.crossover("SPY") is False


def test_max_symbols_overflow_raises():
    t = MovingAverageTracker(short_period=2, long_period=3, max_symbols=2)
    t.record("A", 1.0)
    t.record("B", 2.0)
    with pytest.raises(OverflowError):
        t.record("C", 3.0)


def test_unknown_symbol_returns_none(tracker):
    assert tracker.short_ma("UNKNOWN") is None
    assert tracker.long_ma("UNKNOWN") is None
