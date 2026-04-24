"""Tests for alpaca_stream_cli.trade_counter."""
from datetime import datetime, timezone, timedelta

import pytest

from alpaca_stream_cli.trade_counter import SymbolTradeCounter, TradeCounter


def _ts(offset_seconds: float = 0.0) -> datetime:
    base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    return base + timedelta(seconds=offset_seconds)


# ---------------------------------------------------------------------------
# SymbolTradeCounter
# ---------------------------------------------------------------------------

class TestSymbolTradeCounter:
    def test_invalid_window_raises(self):
        with pytest.raises(ValueError):
            SymbolTradeCounter(window_seconds=0)

    def test_negative_window_raises(self):
        with pytest.raises(ValueError):
            SymbolTradeCounter(window_seconds=-5)

    def test_single_record_returns_one(self):
        ctr = SymbolTradeCounter(window_seconds=60)
        assert ctr.record(_ts(0)) == 1

    def test_multiple_records_within_window(self):
        ctr = SymbolTradeCounter(window_seconds=60)
        ctr.record(_ts(0))
        ctr.record(_ts(10))
        assert ctr.record(_ts(20)) == 3

    def test_old_records_evicted(self):
        ctr = SymbolTradeCounter(window_seconds=30)
        ctr.record(_ts(0))
        ctr.record(_ts(10))
        # at t=40 both earlier stamps are outside the 30-second window
        assert ctr.count(as_of=_ts(40)) == 0

    def test_boundary_record_not_evicted(self):
        ctr = SymbolTradeCounter(window_seconds=30)
        ctr.record(_ts(0))
        # exactly at boundary (t=30): 30 - 30 = 0, stamp at 0 is NOT < 0
        assert ctr.count(as_of=_ts(30)) == 1

    def test_reset_clears_all(self):
        ctr = SymbolTradeCounter(window_seconds=60)
        ctr.record(_ts(0))
        ctr.record(_ts(1))
        ctr.reset()
        assert ctr.count(_ts(2)) == 0


# ---------------------------------------------------------------------------
# TradeCounter
# ---------------------------------------------------------------------------

@pytest.fixture()
def counter():
    return TradeCounter(window_seconds=60, max_symbols=10)


def test_invalid_window_raises():
    with pytest.raises(ValueError):
        TradeCounter(window_seconds=0)


def test_invalid_max_symbols_raises():
    with pytest.raises(ValueError):
        TradeCounter(window_seconds=60, max_symbols=0)


def test_record_normalizes_symbol_to_uppercase(counter):
    counter.record("aapl", _ts(0))
    assert counter.count("AAPL", _ts(1)) == 1


def test_count_unknown_symbol_returns_zero(counter):
    assert counter.count("ZZZZ") == 0


def test_record_returns_rolling_count(counter):
    counter.record("MSFT", _ts(0))
    counter.record("MSFT", _ts(5))
    result = counter.record("MSFT", _ts(10))
    assert result == 3


def test_all_counts_returns_all_symbols(counter):
    counter.record("AAPL", _ts(0))
    counter.record("GOOG", _ts(0))
    counts = counter.all_counts(as_of=_ts(1))
    assert set(counts.keys()) == {"AAPL", "GOOG"}
    assert counts["AAPL"] == 1
    assert counts["GOOG"] == 1


def test_max_symbols_overflow_raises(counter):
    for i in range(10):
        counter.record(f"SYM{i}", _ts(0))
    with pytest.raises(OverflowError):
        counter.record("OVERFLOW", _ts(0))


def test_reset_single_symbol(counter):
    counter.record("AAPL", _ts(0))
    counter.record("GOOG", _ts(0))
    counter.reset("aapl")
    assert counter.count("AAPL", _ts(1)) == 0
    assert counter.count("GOOG", _ts(1)) == 1


def test_reset_all_symbols(counter):
    counter.record("AAPL", _ts(0))
    counter.record("GOOG", _ts(0))
    counter.reset()
    assert counter.count("AAPL", _ts(1)) == 0
    assert counter.count("GOOG", _ts(1)) == 0
