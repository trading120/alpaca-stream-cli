"""Tests for BreakoutTracker."""
import pytest
from alpaca_stream_cli.breakout_tracker import BreakoutTracker, BreakoutResult


@pytest.fixture
def tracker():
    return BreakoutTracker(window=5, max_symbols=10)


def test_invalid_window_raises():
    with pytest.raises(ValueError, match="window"):
        BreakoutTracker(window=1)


def test_invalid_max_symbols_raises():
    with pytest.raises(ValueError, match="max_symbols"):
        BreakoutTracker(window=5, max_symbols=0)


def test_record_normalizes_symbol_to_uppercase(tracker):
    result = tracker.record("aapl", 150.0)
    assert result.symbol == "AAPL"


def test_negative_price_raises(tracker):
    with pytest.raises(ValueError, match="non-negative"):
        tracker.record("AAPL", -1.0)


def test_no_breakout_on_first_record(tracker):
    result = tracker.record("AAPL", 100.0)
    assert not result.breakout_up
    assert not result.breakout_down


def test_upper_lower_set_correctly(tracker):
    tracker.record("AAPL", 100.0)
    tracker.record("AAPL", 105.0)
    tracker.record("AAPL", 98.0)
    result = tracker.record("AAPL", 102.0)
    assert result.upper == 105.0
    assert result.lower == 98.0


def test_breakout_up_detected(tracker):
    for p in [100.0, 101.0, 99.0, 100.5, 100.0]:
        tracker.record("TSLA", p)
    result = tracker.record("TSLA", 105.0)
    assert result.breakout_up
    assert not result.breakout_down
    assert result.pct_above_upper is not None


def test_breakout_down_detected(tracker):
    for p in [100.0, 101.0, 99.0, 100.5, 100.0]:
        tracker.record("TSLA", p)
    result = tracker.record("TSLA", 90.0)
    assert result.breakout_down
    assert not result.breakout_up
    assert result.pct_below_lower is not None


def test_get_before_any_data_returns_none(tracker):
    assert tracker.get("MSFT") is None


def test_get_returns_result_after_record(tracker):
    tracker.record("MSFT", 300.0)
    result = tracker.get("MSFT")
    assert result is not None
    assert result.symbol == "MSFT"


def test_symbols_returns_all_tracked(tracker):
    tracker.record("AAPL", 150.0)
    tracker.record("GOOG", 2800.0)
    assert set(tracker.symbols()) == {"AAPL", "GOOG"}


def test_max_symbols_limit_raises(tracker):
    t = BreakoutTracker(window=3, max_symbols=2)
    t.record("AAPL", 100.0)
    t.record("GOOG", 200.0)
    with pytest.raises(RuntimeError, match="max_symbols"):
        t.record("TSLA", 300.0)


def test_str_breakout_up():
    r = BreakoutResult(
        symbol="AAPL", price=110.0, upper=105.0, lower=95.0,
        breakout_up=True, breakout_down=False,
        pct_above_upper=4.76, pct_below_lower=None,
    )
    assert "UP" in str(r)
    assert "AAPL" in str(r)


def test_str_breakout_down():
    r = BreakoutResult(
        symbol="AAPL", price=90.0, upper=105.0, lower=95.0,
        breakout_up=False, breakout_down=True,
        pct_above_upper=None, pct_below_lower=-5.26,
    )
    assert "DOWN" in str(r)
