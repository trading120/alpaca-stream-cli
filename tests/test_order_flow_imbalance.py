"""Tests for OrderFlowImbalanceTracker and OFIResult."""
import pytest
from alpaca_stream_cli.order_flow_imbalance import (
    OFIResult,
    OrderFlowImbalanceTracker,
)


@pytest.fixture
def tracker() -> OrderFlowImbalanceTracker:
    return OrderFlowImbalanceTracker(window=10, max_symbols=5)


def test_invalid_window_raises():
    with pytest.raises(ValueError):
        OrderFlowImbalanceTracker(window=0)


def test_invalid_max_symbols_raises():
    with pytest.raises(ValueError):
        OrderFlowImbalanceTracker(max_symbols=0)


def test_record_returns_ofi_result(tracker):
    result = tracker.record("AAPL", 150.0, 100, "buy")
    assert isinstance(result, OFIResult)


def test_record_normalizes_symbol_to_uppercase(tracker):
    result = tracker.record("aapl", 150.0, 100, "buy")
    assert result.symbol == "AAPL"


def test_all_buys_ofi_is_one(tracker):
    for _ in range(5):
        result = tracker.record("TSLA", 200.0, 50, "buy")
    assert result.ofi == pytest.approx(1.0)
    assert result.label == "Strong Buy"


def test_all_sells_ofi_is_minus_one(tracker):
    for _ in range(5):
        result = tracker.record("TSLA", 200.0, 50, "sell")
    assert result.ofi == pytest.approx(-1.0)
    assert result.label == "Strong Sell"


def test_equal_buys_sells_ofi_is_zero(tracker):
    tracker.record("MSFT", 300.0, 100, "buy")
    result = tracker.record("MSFT", 300.0, 100, "sell")
    assert result.ofi == pytest.approx(0.0)
    assert result.label == "Neutral"


def test_ofi_weighted_by_volume(tracker):
    tracker.record("NVDA", 400.0, 300, "buy")
    result = tracker.record("NVDA", 400.0, 100, "sell")
    assert result.ofi == pytest.approx(0.5)   # (300-100)/400


def test_window_limits_trade_count(tracker):
    for i in range(15):
        result = tracker.record("AMD", 100.0, 10, "buy")
    assert result.trade_count == 10  # window=10


def test_invalid_side_raises(tracker):
    with pytest.raises(ValueError, match="side"):
        tracker.record("AAPL", 150.0, 100, "unknown")


def test_negative_price_raises(tracker):
    with pytest.raises(ValueError, match="price"):
        tracker.record("AAPL", -1.0, 100, "buy")


def test_negative_volume_raises(tracker):
    with pytest.raises(ValueError, match="volume"):
        tracker.record("AAPL", 150.0, -10, "buy")


def test_get_before_any_record_returns_none(tracker):
    assert tracker.get("AAPL") is None


def test_get_returns_latest_result(tracker):
    tracker.record("GOOG", 100.0, 200, "buy")
    result = tracker.get("GOOG")
    assert result is not None
    assert result.buy_volume == 200


def test_symbols_list_grows(tracker):
    tracker.record("A", 10.0, 1, "buy")
    tracker.record("B", 10.0, 1, "sell")
    assert set(tracker.symbols()) == {"A", "B"}


def test_max_symbols_limit_raises(tracker):
    for i in range(5):
        tracker.record(f"SYM{i}", 10.0, 1, "buy")
    with pytest.raises(RuntimeError, match="max_symbols"):
        tracker.record("EXTRA", 10.0, 1, "buy")
