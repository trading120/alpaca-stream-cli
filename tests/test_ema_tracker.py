"""Tests for alpaca_stream_cli.ema_tracker."""
import pytest
from alpaca_stream_cli.ema_tracker import EMATracker, SymbolEMA


# ---------------------------------------------------------------------------
# SymbolEMA unit tests
# ---------------------------------------------------------------------------

def test_invalid_period_raises():
    with pytest.raises(ValueError):
        SymbolEMA(period=1)


def test_no_value_before_any_record():
    ema = SymbolEMA(period=3)
    # First record seeds the EMA, so we just check sample_count starts at 0
    assert ema.sample_count == 0
    assert ema.value is None


def test_first_record_seeds_ema():
    ema = SymbolEMA(period=3)
    ema.record(100.0)
    assert ema.value == pytest.approx(100.0)


def test_ema_moves_toward_new_price():
    ema = SymbolEMA(period=3)
    ema.record(100.0)
    ema.record(110.0)
    # k = 2/(3+1) = 0.5  =>  110*0.5 + 100*0.5 = 105
    assert ema.value == pytest.approx(105.0)


def test_ema_smoothing_factor():
    ema = SymbolEMA(period=5)
    k = 2.0 / 6.0
    ema.record(50.0)
    ema.record(60.0)
    expected = 60.0 * k + 50.0 * (1 - k)
    assert ema.value == pytest.approx(expected)


def test_negative_price_raises():
    ema = SymbolEMA(period=5)
    with pytest.raises(ValueError):
        ema.record(-1.0)


def test_sample_count_increments():
    ema = SymbolEMA(period=3)
    for i in range(5):
        ema.record(float(i + 1))
    assert ema.sample_count == 5


def test_reset_clears_state():
    ema = SymbolEMA(period=3)
    ema.record(100.0)
    ema.reset()
    assert ema.value is None
    assert ema.sample_count == 0


# ---------------------------------------------------------------------------
# EMATracker tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def tracker():
    return EMATracker(period=3, max_symbols=10)


def test_invalid_period_tracker_raises():
    with pytest.raises(ValueError):
        EMATracker(period=1)


def test_invalid_max_symbols_raises():
    with pytest.raises(ValueError):
        EMATracker(period=3, max_symbols=0)


def test_record_normalizes_symbol_to_uppercase(tracker):
    tracker.record("aapl", 150.0)
    assert tracker.value("AAPL") == pytest.approx(150.0)


def test_value_none_for_unknown_symbol(tracker):
    assert tracker.value("UNKNOWN") is None


def test_sample_count_zero_for_unknown_symbol(tracker):
    assert tracker.sample_count("XYZ") == 0


def test_multiple_symbols_tracked_independently(tracker):
    tracker.record("AAPL", 100.0)
    tracker.record("MSFT", 200.0)
    assert tracker.value("AAPL") == pytest.approx(100.0)
    assert tracker.value("MSFT") == pytest.approx(200.0)


def test_symbols_list_contains_recorded(tracker):
    tracker.record("AAPL", 100.0)
    tracker.record("GOOG", 2800.0)
    assert set(tracker.symbols()) == {"AAPL", "GOOG"}


def test_max_symbols_limit_raises(tracker):
    limited = EMATracker(period=3, max_symbols=2)
    limited.record("A", 1.0)
    limited.record("B", 2.0)
    with pytest.raises(RuntimeError):
        limited.record("C", 3.0)


def test_reset_symbol_clears_ema(tracker):
    tracker.record("AAPL", 150.0)
    tracker.record("AAPL", 160.0)
    tracker.reset("AAPL")
    assert tracker.value("AAPL") is None
    assert tracker.sample_count("AAPL") == 0


def test_reset_unknown_symbol_is_noop(tracker):
    tracker.reset("UNKNOWN")  # should not raise
