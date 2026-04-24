"""Tests for alpaca_stream_cli.trade_rate."""
from datetime import datetime, timezone, timedelta

import pytest

from alpaca_stream_cli.trade_rate import SymbolTradeRate, TradeRateTracker


def _ts(offset_seconds: float = 0.0) -> datetime:
    base = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    return base + timedelta(seconds=offset_seconds)


# --- SymbolTradeRate ---

def test_no_records_returns_zero_rate():
    r = SymbolTradeRate(window_seconds=10.0)
    assert r.rate(now=_ts(0)) == 0.0


def test_no_records_returns_zero_count():
    r = SymbolTradeRate(window_seconds=10.0)
    assert r.count(now=_ts(0)) == 0


def test_single_record_rate():
    r = SymbolTradeRate(window_seconds=10.0)
    r.record(ts=_ts(0))
    assert r.rate(now=_ts(5)) == pytest.approx(1 / 10.0)


def test_multiple_records_rate():
    r = SymbolTradeRate(window_seconds=10.0)
    for i in range(5):
        r.record(ts=_ts(i))
    assert r.rate(now=_ts(9)) == pytest.approx(5 / 10.0)


def test_eviction_removes_old_stamps():
    r = SymbolTradeRate(window_seconds=10.0)
    r.record(ts=_ts(0))
    r.record(ts=_ts(1))
    r.record(ts=_ts(15))  # only this one is in window at t=20
    assert r.count(now=_ts(20)) == 1


def test_all_evicted_returns_zero():
    r = SymbolTradeRate(window_seconds=10.0)
    r.record(ts=_ts(0))
    assert r.rate(now=_ts(100)) == 0.0


# --- TradeRateTracker ---

@pytest.fixture
def tracker():
    return TradeRateTracker(window_seconds=10.0)


def test_invalid_window_raises():
    with pytest.raises(ValueError):
        TradeRateTracker(window_seconds=0)


def test_invalid_max_symbols_raises():
    with pytest.raises(ValueError):
        TradeRateTracker(window_seconds=10.0, max_symbols=0)


def test_unknown_symbol_returns_zero_rate(tracker):
    assert tracker.rate("AAPL", now=_ts(0)) == 0.0


def test_unknown_symbol_returns_zero_count(tracker):
    assert tracker.count("AAPL", now=_ts(0)) == 0


def test_normalizes_symbol_to_uppercase(tracker):
    tracker.record("aapl", ts=_ts(0))
    assert tracker.rate("AAPL", now=_ts(5)) > 0.0


def test_rate_after_record(tracker):
    tracker.record("AAPL", ts=_ts(0))
    tracker.record("AAPL", ts=_ts(1))
    assert tracker.count("AAPL", now=_ts(5)) == 2


def test_all_rates_contains_tracked_symbols(tracker):
    tracker.record("AAPL", ts=_ts(0))
    tracker.record("TSLA", ts=_ts(0))
    rates = tracker.all_rates(now=_ts(5))
    assert "AAPL" in rates and "TSLA" in rates


def test_max_symbols_cap():
    t = TradeRateTracker(window_seconds=10.0, max_symbols=2)
    t.record("AAPL", ts=_ts(0))
    t.record("TSLA", ts=_ts(0))
    t.record("GOOG", ts=_ts(0))  # should be silently dropped
    assert "GOOG" not in t.symbols()


def test_symbols_returns_sorted(tracker):
    tracker.record("TSLA", ts=_ts(0))
    tracker.record("AAPL", ts=_ts(0))
    assert tracker.symbols() == ["AAPL", "TSLA"]
