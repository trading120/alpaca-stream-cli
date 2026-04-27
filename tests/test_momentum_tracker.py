"""Tests for MomentumTracker and SymbolMomentum."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from alpaca_stream_cli.momentum_tracker import MomentumTracker, SymbolMomentum


def _ts(offset_seconds: float = 0.0) -> datetime:
    return datetime.fromtimestamp(1_700_000_000 + offset_seconds, tz=timezone.utc)


# --- SymbolMomentum ---

def test_invalid_window_raises():
    with pytest.raises(ValueError):
        SymbolMomentum(window_seconds=0)


def test_invalid_max_ticks_raises():
    with pytest.raises(ValueError):
        SymbolMomentum(max_ticks=1)


def test_no_roc_before_two_records():
    sm = SymbolMomentum()
    sm.record(100.0, _ts(0))
    assert sm.roc() is None


def test_roc_positive_when_price_rises():
    sm = SymbolMomentum(window_seconds=60)
    sm.record(100.0, _ts(0))
    sm.record(105.0, _ts(10))
    assert sm.roc() == pytest.approx(5.0)


def test_roc_negative_when_price_falls():
    sm = SymbolMomentum(window_seconds=60)
    sm.record(200.0, _ts(0))
    sm.record(190.0, _ts(10))
    assert sm.roc() == pytest.approx(-5.0)


def test_ticks_outside_window_are_pruned():
    sm = SymbolMomentum(window_seconds=30)
    sm.record(100.0, _ts(0))
    sm.record(102.0, _ts(10))
    # This tick is 60s later; the first tick is now outside the 30s window
    sm.record(110.0, _ts(60))
    # Only ticks within 30s of the latest (t=60) should remain
    assert sm.tick_count() == 1
    assert sm.roc() is None


def test_max_ticks_respected():
    sm = SymbolMomentum(window_seconds=3600, max_ticks=5)
    for i in range(10):
        sm.record(100.0 + i, _ts(i))
    assert sm.tick_count() <= 5


def test_negative_price_raises():
    sm = SymbolMomentum()
    with pytest.raises(ValueError):
        sm.record(-1.0, _ts())


def test_latest_price_returns_most_recent():
    sm = SymbolMomentum()
    sm.record(50.0, _ts(0))
    sm.record(75.0, _ts(1))
    assert sm.latest_price() == 75.0


# --- MomentumTracker ---

@pytest.fixture
def tracker() -> MomentumTracker:
    return MomentumTracker(window_seconds=60, max_ticks=100)


def test_record_normalizes_symbol_to_uppercase(tracker):
    tracker.record("aapl", 150.0, _ts())
    assert "AAPL" in tracker.symbols()


def test_roc_returns_none_for_unknown_symbol(tracker):
    assert tracker.roc("UNKNOWN") is None


def test_roc_computed_after_two_records(tracker):
    tracker.record("TSLA", 200.0, _ts(0))
    tracker.record("TSLA", 210.0, _ts(5))
    assert tracker.roc("TSLA") == pytest.approx(5.0)


def test_invalid_max_symbols_raises():
    with pytest.raises(ValueError):
        MomentumTracker(max_symbols=0)


def test_max_symbols_enforced():
    t = MomentumTracker(max_symbols=2)
    t.record("A", 1.0, _ts())
    t.record("B", 2.0, _ts())
    with pytest.raises(RuntimeError):
        t.record("C", 3.0, _ts())


def test_get_returns_none_for_missing_symbol(tracker):
    assert tracker.get("MISSING") is None


def test_get_returns_symbol_momentum(tracker):
    tracker.record("NVDA", 400.0, _ts())
    assert tracker.get("NVDA") is not None
