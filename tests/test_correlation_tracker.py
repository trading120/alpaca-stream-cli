"""Tests for CorrelationTracker."""
import math
import pytest
from alpaca_stream_cli.correlation_tracker import CorrelationTracker, CorrelationResult


@pytest.fixture
def tracker():
    return CorrelationTracker(window=5, max_symbols=10)


def test_invalid_window_raises():
    with pytest.raises(ValueError, match="window"):
        CorrelationTracker(window=1)


def test_invalid_max_symbols_raises():
    with pytest.raises(ValueError, match="max_symbols"):
        CorrelationTracker(max_symbols=0)


def test_correlation_before_any_data_returns_none(tracker):
    result = tracker.correlation("AAPL", "MSFT")
    assert result.correlation is None
    assert result.sample_count == 0


def test_record_normalizes_symbol_to_uppercase(tracker):
    tracker.record("aapl", 150.0)
    tracker.record("msft", 300.0)
    result = tracker.correlation("AAPL", "MSFT")
    assert result.symbol_a == "AAPL"
    assert result.symbol_b == "MSFT"


def test_negative_price_raises(tracker):
    with pytest.raises(ValueError):
        tracker.record("AAPL", -1.0)


def test_perfect_positive_correlation(tracker):
    prices = [100.0, 101.0, 102.0, 103.0, 104.0]
    for p in prices:
        tracker.record("AAPL", p)
        tracker.record("MSFT", p * 2)  # perfectly correlated
    result = tracker.correlation("AAPL", "MSFT")
    assert result.correlation is not None
    assert abs(result.correlation - 1.0) < 1e-9


def test_perfect_negative_correlation(tracker):
    prices = [100.0, 101.0, 102.0, 103.0, 104.0]
    for i, p in enumerate(prices):
        tracker.record("AAPL", p)
        tracker.record("MSFT", 200.0 - p)  # perfectly inverse
    result = tracker.correlation("AAPL", "MSFT")
    assert result.correlation is not None
    assert abs(result.correlation - (-1.0)) < 1e-9


def test_sample_count_reflects_window(tracker):
    for p in [100.0, 101.0, 102.0, 103.0, 104.0, 105.0]:
        tracker.record("AAPL", p)
        tracker.record("MSFT", p)
    result = tracker.correlation("AAPL", "MSFT")
    assert result.sample_count == 5  # window=5


def test_constant_prices_return_none_correlation(tracker):
    for _ in range(5):
        tracker.record("AAPL", 100.0)
        tracker.record("MSFT", 200.0)
    result = tracker.correlation("AAPL", "MSFT")
    assert result.correlation is None


def test_symbols_returns_sorted_list(tracker):
    tracker.record("TSLA", 200.0)
    tracker.record("AAPL", 150.0)
    tracker.record("MSFT", 300.0)
    assert tracker.symbols() == ["AAPL", "MSFT", "TSLA"]


def test_pairs_returns_all_combinations(tracker):
    tracker.record("AAPL", 150.0)
    tracker.record("MSFT", 300.0)
    tracker.record("TSLA", 200.0)
    pairs = tracker.pairs()
    assert ("AAPL", "MSFT") in pairs
    assert ("AAPL", "TSLA") in pairs
    assert ("MSFT", "TSLA") in pairs
    assert len(pairs) == 3


def test_max_symbols_limit_enforced():
    t = CorrelationTracker(window=3, max_symbols=2)
    t.record("AAPL", 100.0)
    t.record("MSFT", 200.0)
    t.record("TSLA", 300.0)  # should be silently ignored
    assert "TSLA" not in t.symbols()
    assert len(t.symbols()) == 2
