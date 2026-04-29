"""Tests for PivotPointTracker and PivotResult."""
import pytest
from alpaca_stream_cli.pivot_points import PivotPointTracker, PivotResult, _calc


@pytest.fixture
def tracker() -> PivotPointTracker:
    return PivotPointTracker()


def test_invalid_max_symbols_raises():
    with pytest.raises(ValueError):
        PivotPointTracker(max_symbols=0)


def test_update_returns_pivot_result(tracker):
    result = tracker.update("AAPL", high=150.0, low=140.0, close=148.0)
    assert isinstance(result, PivotResult)


def test_update_normalizes_symbol_to_uppercase(tracker):
    result = tracker.update("aapl", high=150.0, low=140.0, close=148.0)
    assert result.symbol == "AAPL"


def test_pivot_calculation_correct():
    result = _calc(150.0, 140.0, 148.0)
    expected_pivot = round((150 + 140 + 148) / 3, 4)
    assert result.pivot == expected_pivot


def test_r1_above_pivot():
    result = _calc(150.0, 140.0, 148.0)
    assert result.r1 > result.pivot


def test_s1_below_pivot():
    result = _calc(150.0, 140.0, 148.0)
    assert result.s1 < result.pivot


def test_resistance_levels_ascending():
    result = _calc(150.0, 140.0, 148.0)
    assert result.r1 < result.r2 < result.r3


def test_support_levels_descending():
    result = _calc(150.0, 140.0, 148.0)
    assert result.s1 > result.s2 > result.s3


def test_get_returns_none_for_unknown(tracker):
    assert tracker.get("UNKNOWN") is None


def test_get_returns_stored_result(tracker):
    tracker.update("TSLA", 700.0, 680.0, 695.0)
    assert tracker.get("TSLA") is not None


def test_get_normalizes_case(tracker):
    tracker.update("MSFT", 310.0, 300.0, 308.0)
    assert tracker.get("msft") is not None


def test_update_replaces_existing(tracker):
    tracker.update("AAPL", 150.0, 140.0, 148.0)
    result2 = tracker.update("AAPL", 160.0, 150.0, 158.0)
    assert tracker.get("AAPL").pivot == result2.pivot


def test_high_less_than_low_raises(tracker):
    with pytest.raises(ValueError):
        tracker.update("AAPL", high=130.0, low=150.0, close=140.0)


def test_negative_price_raises(tracker):
    with pytest.raises(ValueError):
        tracker.update("AAPL", high=-10.0, low=-20.0, close=-15.0)


def test_max_symbols_overflow_raises():
    t = PivotPointTracker(max_symbols=2)
    t.update("A", 10, 8, 9)
    t.update("B", 10, 8, 9)
    with pytest.raises(OverflowError):
        t.update("C", 10, 8, 9)


def test_remove_clears_symbol(tracker):
    tracker.update("GOOG", 2800.0, 2750.0, 2780.0)
    tracker.remove("GOOG")
    assert tracker.get("GOOG") is None


def test_all_symbols_lists_stored(tracker):
    tracker.update("AAPL", 150, 140, 148)
    tracker.update("TSLA", 700, 680, 695)
    assert set(tracker.all_symbols()) == {"AAPL", "TSLA"}


def test_clear_removes_all(tracker):
    tracker.update("AAPL", 150, 140, 148)
    tracker.clear()
    assert tracker.all_symbols() == []


def test_nearest_level_pivot(tracker):
    result = tracker.update("AAPL", 150.0, 140.0, 148.0)
    label, level = result.nearest_level(result.pivot)
    assert label == "P"
    assert level == result.pivot


def test_nearest_level_r1(tracker):
    result = tracker.update("AAPL", 150.0, 140.0, 148.0)
    label, level = result.nearest_level(result.r1 + 0.001)
    assert label == "R1"
