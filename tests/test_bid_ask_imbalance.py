"""Tests for BidAskImbalanceTracker and SymbolImbalance."""
import pytest
from alpaca_stream_cli.bid_ask_imbalance import (
    ImbalanceSample,
    SymbolImbalance,
    BidAskImbalanceTracker,
)


# --- ImbalanceSample ---

def test_imbalance_equal_sizes_is_zero():
    s = ImbalanceSample(bid_size=100, ask_size=100)
    assert s.imbalance == pytest.approx(0.0)


def test_imbalance_all_bid_is_one():
    s = ImbalanceSample(bid_size=200, ask_size=0)
    assert s.imbalance == pytest.approx(1.0)


def test_imbalance_all_ask_is_minus_one():
    s = ImbalanceSample(bid_size=0, ask_size=200)
    assert s.imbalance == pytest.approx(-1.0)


def test_imbalance_zero_total_returns_zero():
    s = ImbalanceSample(bid_size=0, ask_size=0)
    assert s.imbalance == pytest.approx(0.0)


# --- SymbolImbalance ---

def test_symbol_imbalance_invalid_max_raises():
    with pytest.raises(ValueError):
        SymbolImbalance(max_samples=0)


def test_symbol_imbalance_latest_none_when_empty():
    si = SymbolImbalance()
    assert si.latest_imbalance() is None


def test_symbol_imbalance_average_none_when_empty():
    si = SymbolImbalance()
    assert si.average_imbalance() is None


def test_symbol_imbalance_records_and_returns_latest():
    si = SymbolImbalance()
    si.record(100, 50)
    si.record(200, 100)
    latest = si.latest_imbalance()
    assert latest == pytest.approx(ImbalanceSample(200, 100).imbalance)


def test_symbol_imbalance_respects_max_samples():
    si = SymbolImbalance(max_samples=3)
    for i in range(5):
        si.record(100, 50)
    assert si.sample_count() == 3


def test_symbol_imbalance_average_correct():
    si = SymbolImbalance()
    si.record(100, 0)   # imbalance = 1.0
    si.record(0, 100)   # imbalance = -1.0
    assert si.average_imbalance() == pytest.approx(0.0)


# --- BidAskImbalanceTracker ---

def test_tracker_normalizes_symbol_to_uppercase():
    t = BidAskImbalanceTracker()
    t.record("aapl", 100, 50)
    assert t.latest_imbalance("AAPL") is not None


def test_tracker_unknown_symbol_returns_none():
    t = BidAskImbalanceTracker()
    assert t.latest_imbalance("MSFT") is None


def test_tracker_invalid_max_symbols_raises():
    with pytest.raises(ValueError):
        BidAskImbalanceTracker(max_symbols=0)


def test_tracker_max_symbols_raises_on_overflow():
    t = BidAskImbalanceTracker(max_symbols=2)
    t.record("AAPL", 100, 50)
    t.record("MSFT", 100, 50)
    with pytest.raises(RuntimeError):
        t.record("TSLA", 100, 50)


def test_tracker_symbols_list():
    t = BidAskImbalanceTracker()
    t.record("AAPL", 100, 50)
    t.record("MSFT", 200, 100)
    assert set(t.symbols()) == {"AAPL", "MSFT"}


def test_tracker_average_imbalance_unknown_returns_none():
    t = BidAskImbalanceTracker()
    assert t.average_imbalance("GOOG") is None
