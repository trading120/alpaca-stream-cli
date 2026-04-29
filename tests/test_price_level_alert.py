"""Tests for PriceLevelAlert."""
import pytest
from alpaca_stream_cli.price_level_alert import PriceLevelAlert, LevelCrossResult


@pytest.fixture
def tracker() -> PriceLevelAlert:
    return PriceLevelAlert(round_increments=(1.0, 5.0))


def test_invalid_increments_raises() -> None:
    with pytest.raises(ValueError):
        PriceLevelAlert(round_increments=())


def test_invalid_negative_increment_raises() -> None:
    with pytest.raises(ValueError):
        PriceLevelAlert(round_increments=(-1.0,))


def test_first_record_returns_no_crossings(tracker: PriceLevelAlert) -> None:
    results = tracker.record("AAPL", 149.50)
    assert results == []


def test_no_crossing_within_same_integer(tracker: PriceLevelAlert) -> None:
    tracker.record("AAPL", 149.10)
    results = tracker.record("AAPL", 149.80)
    assert all(r.level_type != "round" or r.level != 150.0 for r in results)


def test_crosses_round_level_upward(tracker: PriceLevelAlert) -> None:
    tracker.record("AAPL", 149.80)
    results = tracker.record("AAPL", 150.20)
    round_crosses = [r for r in results if r.level_type == "round" and r.level == 150.0]
    assert len(round_crosses) == 1
    assert round_crosses[0].direction == "above"
    assert round_crosses[0].symbol == "AAPL"


def test_crosses_round_level_downward(tracker: PriceLevelAlert) -> None:
    tracker.record("AAPL", 150.20)
    results = tracker.record("AAPL", 149.80)
    round_crosses = [r for r in results if r.level_type == "round" and r.level == 150.0]
    assert len(round_crosses) == 1
    assert round_crosses[0].direction == "below"


def test_crosses_multiple_round_levels(tracker: PriceLevelAlert) -> None:
    tracker.record("AAPL", 148.50)
    results = tracker.record("AAPL", 151.50)
    levels = {r.level for r in results if r.level_type == "round"}
    assert 149.0 in levels
    assert 150.0 in levels
    assert 151.0 in levels


def test_symbol_normalized_to_uppercase(tracker: PriceLevelAlert) -> None:
    tracker.record("aapl", 149.80)
    results = tracker.record("aapl", 150.20)
    assert all(r.symbol == "AAPL" for r in results)


def test_day_high_crossing_detected(tracker: PriceLevelAlert) -> None:
    tracker.update_day_range("TSLA", high=200.0, low=190.0)
    tracker.record("TSLA", 199.50)
    results = tracker.record("TSLA", 200.50)
    day_high_crosses = [r for r in results if r.level_type == "day_high"]
    assert len(day_high_crosses) == 1
    assert day_high_crosses[0].direction == "above"


def test_day_low_crossing_detected(tracker: PriceLevelAlert) -> None:
    tracker.update_day_range("TSLA", high=200.0, low=190.0)
    tracker.record("TSLA", 190.50)
    results = tracker.record("TSLA", 189.50)
    day_low_crosses = [r for r in results if r.level_type == "day_low"]
    assert len(day_low_crosses) == 1
    assert day_low_crosses[0].direction == "below"


def test_update_day_range_invalid_raises(tracker: PriceLevelAlert) -> None:
    with pytest.raises(ValueError):
        tracker.update_day_range("AAPL", high=190.0, low=200.0)


def test_negative_price_raises(tracker: PriceLevelAlert) -> None:
    with pytest.raises(ValueError):
        tracker.record("AAPL", -1.0)


def test_reset_clears_state(tracker: PriceLevelAlert) -> None:
    tracker.record("AAPL", 149.80)
    tracker.reset("AAPL")
    results = tracker.record("AAPL", 150.20)
    assert results == []


def test_str_representation() -> None:
    result = LevelCrossResult("AAPL", 150.20, 150.0, "above", "round")
    s = str(result)
    assert "AAPL" in s
    assert "above" in s
    assert "150.00" in s


def test_independent_symbols_do_not_interfere(tracker: PriceLevelAlert) -> None:
    tracker.record("AAPL", 149.80)
    tracker.record("MSFT", 299.80)
    aapl_results = tracker.record("AAPL", 150.20)
    msft_results = tracker.record("MSFT", 300.20)
    assert all(r.symbol == "AAPL" for r in aapl_results)
    assert all(r.symbol == "MSFT" for r in msft_results)
