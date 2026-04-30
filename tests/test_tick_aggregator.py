"""Tests for TickAggregator and SymbolAggregator."""
from __future__ import annotations

import pytest
from datetime import datetime, timezone

from alpaca_stream_cli.tick_aggregator import (
    TickAggregator,
    SymbolAggregator,
    TickBucket,
)


def _ts(h: int, m: int, s: int = 0) -> datetime:
    return datetime(2024, 1, 15, h, m, s, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# SymbolAggregator
# ---------------------------------------------------------------------------

def test_invalid_interval_raises():
    with pytest.raises(ValueError):
        SymbolAggregator("AAPL", 0)


def test_negative_interval_raises():
    with pytest.raises(ValueError):
        SymbolAggregator("AAPL", -10)


def test_first_record_returns_none():
    agg = SymbolAggregator("AAPL", 60)
    result = agg.record(150.0, 100.0, _ts(9, 30))
    assert result is None


def test_same_bucket_no_completion():
    agg = SymbolAggregator("AAPL", 60)
    agg.record(150.0, 100.0, _ts(9, 30, 0))
    result = agg.record(151.0, 50.0, _ts(9, 30, 45))
    assert result is None


def test_new_bucket_returns_completed():
    agg = SymbolAggregator("AAPL", 60)
    agg.record(150.0, 100.0, _ts(9, 30, 0))
    agg.record(151.0, 50.0, _ts(9, 30, 30))
    completed = agg.record(152.0, 200.0, _ts(9, 31, 0))
    assert completed is not None
    assert isinstance(completed, TickBucket)


def test_completed_bucket_ohlc_correct():
    agg = SymbolAggregator("AAPL", 60)
    agg.record(150.0, 100.0, _ts(9, 30, 0))
    agg.record(155.0, 50.0, _ts(9, 30, 20))
    agg.record(148.0, 80.0, _ts(9, 30, 40))
    completed = agg.record(152.0, 60.0, _ts(9, 31, 0))
    assert completed.open == 150.0
    assert completed.high == 155.0
    assert completed.low == 148.0
    assert completed.close == 148.0
    assert completed.volume == 230.0
    assert completed.trade_count == 3


def test_negative_price_raises():
    agg = SymbolAggregator("AAPL", 60)
    with pytest.raises(ValueError):
        agg.record(-1.0, 100.0, _ts(9, 30))


def test_negative_volume_raises():
    agg = SymbolAggregator("AAPL", 60)
    with pytest.raises(ValueError):
        agg.record(150.0, -1.0, _ts(9, 30))


def test_symbol_normalized_to_uppercase():
    agg = SymbolAggregator("aapl", 60)
    agg.record(150.0, 100.0, _ts(9, 30, 0))
    completed = agg.record(151.0, 50.0, _ts(9, 31, 0))
    assert completed.symbol == "AAPL"


def test_change_and_change_pct():
    agg = SymbolAggregator("AAPL", 60)
    agg.record(100.0, 100.0, _ts(9, 30, 0))
    completed = agg.record(110.0, 50.0, _ts(9, 31, 0))
    assert completed.change == pytest.approx(10.0)
    assert completed.change_pct == pytest.approx(10.0)


# ---------------------------------------------------------------------------
# TickAggregator (multi-symbol)
# ---------------------------------------------------------------------------

@pytest.fixture
def tracker():
    return TickAggregator(interval_seconds=60)


def test_invalid_interval_raises_multi():
    with pytest.raises(ValueError):
        TickAggregator(interval_seconds=0)


def test_invalid_max_symbols_raises():
    with pytest.raises(ValueError):
        TickAggregator(interval_seconds=60, max_symbols=0)


def test_record_returns_none_within_bucket(tracker):
    result = tracker.record("AAPL", 150.0, 100.0, _ts(9, 30, 0))
    assert result is None


def test_record_normalizes_symbol(tracker):
    tracker.record("aapl", 150.0, 100.0, _ts(9, 30, 0))
    assert "AAPL" in tracker.symbols()


def test_completed_stored_for_symbol(tracker):
    tracker.record("AAPL", 150.0, 100.0, _ts(9, 30, 0))
    tracker.record("AAPL", 152.0, 50.0, _ts(9, 31, 0))
    buckets = tracker.completed("AAPL")
    assert len(buckets) == 1
    assert buckets[0].symbol == "AAPL"


def test_multiple_symbols_independent(tracker):
    tracker.record("AAPL", 150.0, 100.0, _ts(9, 30, 0))
    tracker.record("TSLA", 200.0, 200.0, _ts(9, 30, 0))
    tracker.record("AAPL", 151.0, 50.0, _ts(9, 31, 0))
    assert len(tracker.completed("AAPL")) == 1
    assert len(tracker.completed("TSLA")) == 0


def test_max_symbols_not_exceeded():
    t = TickAggregator(interval_seconds=60, max_symbols=2)
    t.record("AAPL", 150.0, 100.0, _ts(9, 30))
    t.record("TSLA", 200.0, 100.0, _ts(9, 30))
    result = t.record("MSFT", 300.0, 100.0, _ts(9, 30))
    assert result is None
    assert "MSFT" not in t.symbols()


def test_completed_unknown_symbol_returns_empty(tracker):
    assert tracker.completed("UNKNOWN") == []
