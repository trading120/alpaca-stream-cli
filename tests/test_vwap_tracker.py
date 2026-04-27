"""Tests for VWAPTracker and SymbolVWAP."""
import pytest
from alpaca_stream_cli.vwap_tracker import SymbolVWAP, VWAPTracker


# --- SymbolVWAP unit tests ---

def test_no_value_before_any_record():
    acc = SymbolVWAP()
    assert acc.value is None


def test_single_record_vwap_equals_price():
    acc = SymbolVWAP()
    acc.record(100.0, 500)
    assert acc.value == pytest.approx(100.0)


def test_two_records_weighted_correctly():
    acc = SymbolVWAP()
    acc.record(100.0, 100)
    acc.record(200.0, 100)
    assert acc.value == pytest.approx(150.0)


def test_higher_volume_weight_pulls_vwap():
    acc = SymbolVWAP()
    acc.record(100.0, 900)
    acc.record(200.0, 100)
    assert acc.value == pytest.approx(110.0)


def test_zero_volume_record_does_not_affect_vwap():
    acc = SymbolVWAP()
    acc.record(100.0, 200)
    acc.record(999.0, 0)
    assert acc.value == pytest.approx(100.0)


def test_negative_price_raises():
    acc = SymbolVWAP()
    with pytest.raises(ValueError, match="price"):
        acc.record(-1.0, 100)


def test_negative_volume_raises():
    acc = SymbolVWAP()
    with pytest.raises(ValueError, match="volume"):
        acc.record(50.0, -10)


def test_reset_clears_accumulator():
    acc = SymbolVWAP()
    acc.record(100.0, 500)
    acc.reset()
    assert acc.value is None
    assert acc.trade_count == 0


def test_trade_count_increments():
    acc = SymbolVWAP()
    acc.record(10.0, 1)
    acc.record(20.0, 1)
    assert acc.trade_count == 2


# --- VWAPTracker tests ---

def test_invalid_max_symbols_raises():
    with pytest.raises(ValueError):
        VWAPTracker(max_symbols=0)


def test_record_returns_vwap():
    t = VWAPTracker()
    result = t.record("AAPL", 150.0, 100)
    assert result == pytest.approx(150.0)


def test_record_normalizes_symbol_to_uppercase():
    t = VWAPTracker()
    t.record("aapl", 150.0, 100)
    assert t.get("AAPL") == pytest.approx(150.0)


def test_get_unknown_symbol_returns_none():
    t = VWAPTracker()
    assert t.get("ZZZZ") is None


def test_max_symbols_limit_returns_none():
    t = VWAPTracker(max_symbols=1)
    t.record("AAPL", 100.0, 50)
    result = t.record("MSFT", 200.0, 50)
    assert result is None


def test_reset_symbol_clears_data():
    t = VWAPTracker()
    t.record("AAPL", 100.0, 200)
    t.reset("AAPL")
    assert t.get("AAPL") is None


def test_reset_all_clears_all_symbols():
    t = VWAPTracker()
    t.record("AAPL", 100.0, 100)
    t.record("MSFT", 200.0, 100)
    t.reset_all()
    assert t.get("AAPL") is None
    assert t.get("MSFT") is None


def test_tracked_symbols_lists_known_symbols():
    t = VWAPTracker()
    t.record("AAPL", 100.0, 10)
    t.record("TSLA", 700.0, 10)
    assert set(t.tracked_symbols) == {"AAPL", "TSLA"}
