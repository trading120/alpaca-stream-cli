"""Tests for PriceBandTracker."""
import pytest
from alpaca_stream_cli.price_band_tracker import PriceBandTracker, BandResult


def test_invalid_proximity_pct_raises():
    with pytest.raises(ValueError):
        PriceBandTracker(proximity_pct=-0.01)


def test_invalid_max_symbols_raises():
    with pytest.raises(ValueError):
        PriceBandTracker(max_symbols=0)


def test_record_returns_band_result():
    tracker = PriceBandTracker()
    result = tracker.record("aapl", 175.0, 180.0, 170.0)
    assert isinstance(result, BandResult)
    assert result.symbol == "AAPL"


def test_record_normalizes_symbol_to_uppercase():
    tracker = PriceBandTracker()
    result = tracker.record("tsla", 200.0, 210.0, 190.0)
    assert result.symbol == "TSLA"


def test_band_range_calculated_correctly():
    tracker = PriceBandTracker()
    result = tracker.record("GOOG", 150.0, 160.0, 140.0)
    assert result.band_range == pytest.approx(20.0)


def test_pct_from_low_at_midpoint():
    tracker = PriceBandTracker()
    result = tracker.record("MSFT", 150.0, 160.0, 140.0)
    assert result.pct_from_low == pytest.approx(0.5)


def test_pct_from_low_at_high():
    tracker = PriceBandTracker()
    result = tracker.record("MSFT", 160.0, 160.0, 140.0)
    assert result.pct_from_low == pytest.approx(1.0)


def test_pct_from_low_at_low():
    tracker = PriceBandTracker()
    result = tracker.record("MSFT", 140.0, 160.0, 140.0)
    assert result.pct_from_low == pytest.approx(0.0)


def test_pct_from_low_none_when_range_zero():
    tracker = PriceBandTracker()
    result = tracker.record("MSFT", 150.0, 150.0, 150.0)
    assert result.pct_from_low is None


def test_near_high_true_when_within_proximity():
    tracker = PriceBandTracker(proximity_pct=0.02)
    result = tracker.record("AAPL", 179.0, 180.0, 160.0)
    assert result.near_high is True


def test_near_high_false_when_far_from_high():
    tracker = PriceBandTracker(proximity_pct=0.02)
    result = tracker.record("AAPL", 170.0, 180.0, 160.0)
    assert result.near_high is False


def test_near_low_true_when_within_proximity():
    tracker = PriceBandTracker(proximity_pct=0.02)
    result = tracker.record("AAPL", 161.0, 180.0, 160.0)
    assert result.near_low is True


def test_near_low_false_when_far_from_low():
    tracker = PriceBandTracker(proximity_pct=0.02)
    result = tracker.record("AAPL", 170.0, 180.0, 160.0)
    assert result.near_low is False


def test_negative_price_raises():
    tracker = PriceBandTracker()
    with pytest.raises(ValueError):
        tracker.record("AAPL", -1.0, 10.0, 5.0)


def test_high_less_than_low_raises():
    tracker = PriceBandTracker()
    with pytest.raises(ValueError):
        tracker.record("AAPL", 5.0, 4.0, 6.0)


def test_get_returns_none_for_unknown_symbol():
    tracker = PriceBandTracker()
    assert tracker.get("UNKNOWN") is None


def test_get_returns_result_after_record():
    tracker = PriceBandTracker()
    tracker.record("SPY", 450.0, 460.0, 440.0)
    result = tracker.get("spy")
    assert result is not None
    assert result.symbol == "SPY"


def test_remove_existing_symbol_returns_true():
    tracker = PriceBandTracker()
    tracker.record("QQQ", 380.0, 390.0, 370.0)
    assert tracker.remove("QQQ") is True
    assert tracker.get("QQQ") is None


def test_remove_unknown_symbol_returns_false():
    tracker = PriceBandTracker()
    assert tracker.remove("FAKE") is False


def test_max_symbols_overflow_raises():
    tracker = PriceBandTracker(max_symbols=2)
    tracker.record("A", 10.0, 11.0, 9.0)
    tracker.record("B", 20.0, 21.0, 19.0)
    with pytest.raises(OverflowError):
        tracker.record("C", 30.0, 31.0, 29.0)


def test_clear_removes_all_symbols():
    tracker = PriceBandTracker()
    tracker.record("AAPL", 175.0, 180.0, 170.0)
    tracker.record("GOOG", 140.0, 145.0, 135.0)
    tracker.clear()
    assert tracker.symbols() == []
