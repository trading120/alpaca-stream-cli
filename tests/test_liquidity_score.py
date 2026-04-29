"""Tests for LiquidityScoreTracker and LiquidityResult."""
from __future__ import annotations

import pytest

from alpaca_stream_cli.liquidity_score import LiquidityResult, LiquidityScoreTracker


@pytest.fixture()
def tracker() -> LiquidityScoreTracker:
    return LiquidityScoreTracker()


def test_invalid_max_symbols_raises():
    with pytest.raises(ValueError):
        LiquidityScoreTracker(max_symbols=0)


def test_get_before_any_update_returns_none(tracker):
    assert tracker.get("AAPL") is None


def test_update_spread_normalizes_symbol(tracker):
    tracker.update_spread("aapl", 0.2)
    result = tracker.get("AAPL")
    assert result is not None


def test_update_volume_normalizes_symbol(tracker):
    tracker.update_volume("msft", 0.5)
    result = tracker.get("MSFT")
    assert result is not None


def test_update_rate_normalizes_symbol(tracker):
    tracker.update_rate("tsla", 0.8)
    result = tracker.get("TSLA")
    assert result is not None


def test_spread_out_of_range_raises(tracker):
    with pytest.raises(ValueError):
        tracker.update_spread("AAPL", 1.5)


def test_volume_out_of_range_raises(tracker):
    with pytest.raises(ValueError):
        tracker.update_volume("AAPL", -0.1)


def test_rate_out_of_range_raises(tracker):
    with pytest.raises(ValueError):
        tracker.update_rate("AAPL", 2.0)


def test_score_components_sum_to_score(tracker):
    tracker.update_spread("AAPL", 0.2)
    tracker.update_volume("AAPL", 0.6)
    tracker.update_rate("AAPL", 0.8)
    result = tracker.get("AAPL")
    assert result is not None
    total = result.spread_component + result.volume_component + result.rate_component
    assert abs(total - result.score) < 1e-6


def test_high_liquidity_label(tracker):
    tracker.update_spread("AAPL", 0.0)
    tracker.update_volume("AAPL", 1.0)
    tracker.update_rate("AAPL", 1.0)
    result = tracker.get("AAPL")
    assert result is not None
    assert result.label == "HIGH"


def test_low_liquidity_label(tracker):
    tracker.update_spread("AAPL", 1.0)
    tracker.update_volume("AAPL", 0.0)
    tracker.update_rate("AAPL", 0.0)
    result = tracker.get("AAPL")
    assert result is not None
    assert result.label == "LOW"


def test_medium_liquidity_label(tracker):
    tracker.update_spread("AAPL", 0.5)
    tracker.update_volume("AAPL", 0.5)
    tracker.update_rate("AAPL", 0.5)
    result = tracker.get("AAPL")
    assert result is not None
    assert result.label == "MED"


def test_all_results_returns_all_tracked(tracker):
    for sym in ("AAPL", "MSFT", "TSLA"):
        tracker.update_spread(sym, 0.3)
    results = tracker.all_results()
    assert len(results) == 3


def test_max_symbols_overflow_raises():
    t = LiquidityScoreTracker(max_symbols=2)
    t.update_spread("AAPL", 0.1)
    t.update_spread("MSFT", 0.2)
    with pytest.raises(OverflowError):
        t.update_spread("TSLA", 0.3)


def test_update_existing_symbol_does_not_grow_tracker():
    t = LiquidityScoreTracker(max_symbols=1)
    t.update_spread("AAPL", 0.1)
    t.update_spread("AAPL", 0.2)  # should not raise
    assert len(t.all_results()) == 1
