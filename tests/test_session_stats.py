"""Tests for session_stats module."""

import pytest
from alpaca_stream_cli.session_stats import SessionStats, SymbolStats


@pytest.fixture
def stats():
    return SessionStats()


def test_update_sets_session_open_on_first_trade(stats):
    s = stats.update("AAPL", 150.0, 100)
    assert s.session_open == 150.0


def test_update_does_not_change_open_on_subsequent_trades(stats):
    stats.update("AAPL", 150.0, 100)
    s = stats.update("AAPL", 155.0, 200)
    assert s.session_open == 150.0


def test_high_low_tracked_correctly(stats):
    stats.update("AAPL", 150.0)
    stats.update("AAPL", 160.0)
    stats.update("AAPL", 145.0)
    s = stats.get("AAPL")
    assert s.high == 160.0
    assert s.low == 145.0


def test_volume_accumulates(stats):
    stats.update("AAPL", 150.0, 100)
    stats.update("AAPL", 151.0, 250)
    s = stats.get("AAPL")
    assert s.total_volume == 350


def test_trade_count_increments(stats):
    stats.update("AAPL", 150.0)
    stats.update("AAPL", 151.0)
    s = stats.get("AAPL")
    assert s.trade_count == 2


def test_session_change_calculated(stats):
    stats.update("AAPL", 100.0)
    stats.update("AAPL", 110.0)
    s = stats.get("AAPL")
    assert s.session_change == pytest.approx(10.0)
    assert s.session_change_pct == pytest.approx(10.0)


def test_normalizes_symbol_case(stats):
    stats.update("aapl", 150.0)
    s = stats.get("AAPL")
    assert s is not None
    assert s.symbol == "AAPL"


def test_get_unknown_symbol_returns_none(stats):
    assert stats.get("UNKNOWN") is None


def test_reset_removes_symbol(stats):
    stats.update("AAPL", 150.0)
    stats.reset("AAPL")
    assert stats.get("AAPL") is None


def test_reset_all_clears_everything(stats):
    stats.update("AAPL", 150.0)
    stats.update("MSFT", 300.0)
    stats.reset_all()
    assert stats.all_symbols() == []


def test_invalid_price_ignored(stats):
    s = stats.update("AAPL", -1.0)
    assert s.session_open is None
    assert s.trade_count == 0
