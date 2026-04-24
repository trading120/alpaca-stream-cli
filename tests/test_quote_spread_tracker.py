"""Tests for QuoteSpreadTracker and SymbolSpreadTracker."""

from datetime import datetime

import pytest

from alpaca_stream_cli.quote_spread_tracker import (
    QuoteSpreadTracker,
    SymbolSpreadTracker,
    _SpreadSample,
)


# ── SymbolSpreadTracker ──────────────────────────────────────────────────────


def test_invalid_max_samples_raises():
    with pytest.raises(ValueError):
        SymbolSpreadTracker(max_samples=0)


def test_record_returns_sample():
    t = SymbolSpreadTracker()
    s = t.record(bid=100.0, ask=100.10)
    assert isinstance(s, _SpreadSample)
    assert s.bid == 100.0
    assert s.ask == 100.10


def test_spread_calculation():
    t = SymbolSpreadTracker()
    s = t.record(bid=99.90, ask=100.10)
    assert abs(s.spread - 0.20) < 1e-9


def test_mid_calculation():
    t = SymbolSpreadTracker()
    s = t.record(bid=100.0, ask=102.0)
    assert s.mid == 101.0


def test_spread_pct_calculation():
    t = SymbolSpreadTracker()
    s = t.record(bid=100.0, ask=101.0)
    # spread=1, mid=100.5 → pct ≈ 0.995...
    assert s.spread_pct is not None
    assert abs(s.spread_pct - (1.0 / 100.5) * 100) < 1e-6


def test_spread_pct_none_when_mid_zero():
    t = SymbolSpreadTracker()
    s = t.record(bid=0.0, ask=0.0)
    assert s.spread_pct is None


def test_latest_returns_most_recent():
    t = SymbolSpreadTracker()
    t.record(bid=10.0, ask=10.5)
    t.record(bid=11.0, ask=11.5)
    assert t.latest().bid == 11.0


def test_latest_none_when_empty():
    t = SymbolSpreadTracker()
    assert t.latest() is None


def test_max_samples_enforced():
    t = SymbolSpreadTracker(max_samples=3)
    for i in range(5):
        t.record(bid=float(i), ask=float(i) + 0.1)
    assert len(t) == 3


def test_average_spread_correct():
    t = SymbolSpreadTracker()
    t.record(bid=100.0, ask=100.20)  # spread 0.20
    t.record(bid=100.0, ask=100.40)  # spread 0.40
    assert abs(t.average_spread() - 0.30) < 1e-9


def test_average_spread_none_when_empty():
    t = SymbolSpreadTracker()
    assert t.average_spread() is None


def test_average_spread_pct_none_when_empty():
    t = SymbolSpreadTracker()
    assert t.average_spread_pct() is None


# ── QuoteSpreadTracker ───────────────────────────────────────────────────────


def test_record_normalizes_symbol_to_uppercase():
    tracker = QuoteSpreadTracker()
    tracker.record("aapl", bid=150.0, ask=150.10)
    assert tracker.get("AAPL") is not None
    assert tracker.get("aapl") is not None


def test_symbols_sorted():
    tracker = QuoteSpreadTracker()
    tracker.record("TSLA", bid=200.0, ask=200.5)
    tracker.record("AAPL", bid=150.0, ask=150.1)
    assert tracker.symbols() == ["AAPL", "TSLA"]


def test_remove_symbol():
    tracker = QuoteSpreadTracker()
    tracker.record("AAPL", bid=150.0, ask=150.1)
    tracker.remove("AAPL")
    assert tracker.get("AAPL") is None


def test_clear_removes_all():
    tracker = QuoteSpreadTracker()
    tracker.record("AAPL", bid=150.0, ask=150.1)
    tracker.record("TSLA", bid=200.0, ask=200.5)
    tracker.clear()
    assert tracker.symbols() == []


def test_invalid_max_samples_raises_on_tracker():
    with pytest.raises(ValueError):
        QuoteSpreadTracker(max_samples=0)
