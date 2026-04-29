"""Tests for GapTracker and GapResult."""
import pytest
from alpaca_stream_cli.gap_tracker import GapTracker, GapResult


@pytest.fixture
def tracker() -> GapTracker:
    return GapTracker(max_symbols=10)


def test_invalid_max_symbols_raises():
    with pytest.raises(ValueError):
        GapTracker(max_symbols=0)


def test_record_open_without_prev_close_returns_none(tracker):
    result = tracker.record_open("AAPL", 150.0)
    assert result is None


def test_get_before_any_data_returns_none(tracker):
    assert tracker.get("AAPL") is None


def test_set_prev_close_then_record_open_returns_result(tracker):
    tracker.set_prev_close("AAPL", 148.0)
    result = tracker.record_open("AAPL", 150.0)
    assert isinstance(result, GapResult)
    assert result.symbol == "AAPL"


def test_gap_up_calculated_correctly(tracker):
    tracker.set_prev_close("AAPL", 100.0)
    result = tracker.record_open("AAPL", 105.0)
    assert result.gap == pytest.approx(5.0)
    assert result.gap_pct == pytest.approx(5.0)
    assert result.is_gap_up is True
    assert result.is_gap_down is False


def test_gap_down_calculated_correctly(tracker):
    tracker.set_prev_close("MSFT", 200.0)
    result = tracker.record_open("MSFT", 190.0)
    assert result.gap == pytest.approx(-10.0)
    assert result.gap_pct == pytest.approx(-5.0)
    assert result.is_gap_down is True


def test_symbol_normalized_to_uppercase(tracker):
    tracker.set_prev_close("tsla", 250.0)
    result = tracker.record_open("TSLA", 255.0)
    assert result is not None
    assert result.symbol == "TSLA"


def test_gap_not_filled_initially(tracker):
    tracker.set_prev_close("AAPL", 100.0)
    result = tracker.record_open("AAPL", 105.0)
    assert result.filled is False


def test_gap_up_filled_when_price_drops_to_prev_close(tracker):
    tracker.set_prev_close("AAPL", 100.0)
    tracker.record_open("AAPL", 105.0)
    filled = tracker.check_fill("AAPL", 99.5)
    assert filled is True
    assert tracker.get("AAPL").filled is True


def test_gap_down_filled_when_price_rises_to_prev_close(tracker):
    tracker.set_prev_close("MSFT", 200.0)
    tracker.record_open("MSFT", 190.0)
    filled = tracker.check_fill("MSFT", 200.5)
    assert filled is True


def test_gap_up_not_filled_while_above_prev_close(tracker):
    tracker.set_prev_close("AAPL", 100.0)
    tracker.record_open("AAPL", 105.0)
    filled = tracker.check_fill("AAPL", 102.0)
    assert filled is False


def test_check_fill_without_result_returns_false(tracker):
    assert tracker.check_fill("AAPL", 100.0) is False


def test_all_results_returns_only_symbols_with_open(tracker):
    tracker.set_prev_close("AAPL", 100.0)
    tracker.set_prev_close("MSFT", 200.0)
    tracker.record_open("AAPL", 105.0)
    results = tracker.all_results()
    assert "AAPL" in results
    assert "MSFT" not in results


def test_new_prev_close_resets_result(tracker):
    tracker.set_prev_close("AAPL", 100.0)
    tracker.record_open("AAPL", 105.0)
    tracker.set_prev_close("AAPL", 110.0)
    assert tracker.get("AAPL") is None


def test_negative_prev_close_raises(tracker):
    with pytest.raises(ValueError):
        tracker.set_prev_close("AAPL", -1.0)


def test_negative_open_price_raises(tracker):
    tracker.set_prev_close("AAPL", 100.0)
    with pytest.raises(ValueError):
        tracker.record_open("AAPL", -5.0)
