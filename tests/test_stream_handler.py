"""Tests for StreamHandler message processing."""

from unittest.mock import MagicMock

import pytest

from alpaca_stream_cli.alerts import AlertConfig, AlertEngine
from alpaca_stream_cli.display import QuoteSnapshot
from alpaca_stream_cli.stream_handler import StreamHandler
from alpaca_stream_cli.watchlist import Watchlist


@pytest.fixture
def watchlist():
    wl = Watchlist()
    wl.add("AAPL")
    wl.add("TSLA")
    return wl


@pytest.fixture
def alert_engine():
    alerts = [
        AlertConfig(symbol="AAPL", condition="above", threshold=155.0),
    ]
    return AlertEngine(alerts)


@pytest.fixture
def handler(watchlist, alert_engine):
    render_mock = MagicMock()
    return StreamHandler(watchlist, alert_engine, on_render=render_mock), render_mock


def test_trade_message_updates_last_price(handler):
    sh, render = handler
    sh.handle_message({"T": "t", "S": "AAPL", "p": "150.50", "s": "100"})
    assert sh.quotes["AAPL"].last == 150.50


def test_trade_message_accumulates_volume(handler):
    sh, render = handler
    sh.handle_message({"T": "t", "S": "AAPL", "p": "150.00", "s": "200"})
    sh.handle_message({"T": "t", "S": "AAPL", "p": "151.00", "s": "300"})
    assert sh.quotes["AAPL"].volume == 500


def test_quote_message_updates_bid_ask(handler):
    sh, render = handler
    sh.handle_message({"T": "q", "S": "AAPL", "bp": "149.90", "ap": "150.10"})
    snap = sh.quotes["AAPL"]
    assert snap.bid == 149.90
    assert snap.ask == 150.10


def test_unknown_symbol_ignored(handler):
    sh, render = handler
    sh.handle_message({"T": "t", "S": "UNKNOWN", "p": "50.00", "s": "10"})
    assert "UNKNOWN" not in sh.quotes


def test_render_called_on_trade(handler):
    sh, render = handler
    sh.handle_message({"T": "t", "S": "AAPL", "p": "150.00", "s": "50"})
    render.assert_called_once()


def test_change_pct_calculated_with_prev_close(handler):
    sh, render = handler
    sh.set_prev_close("AAPL", 148.00)
    sh.handle_message({"T": "t", "S": "AAPL", "p": "150.48", "s": "100"})
    snap = sh.quotes["AAPL"]
    assert snap.change_pct == pytest.approx(1.675, rel=1e-2)


def test_alert_triggers_on_threshold_breach(handler):
    sh, render = handler
    sh.handle_message({"T": "t", "S": "AAPL", "p": "160.00", "s": "100"})
    _, triggered_list = render.call_args[0]
    assert any(a.symbol == "AAPL" for a in triggered_list)
