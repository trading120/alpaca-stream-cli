"""Tests for alpaca_stream_cli/status_bar.py"""

from unittest.mock import MagicMock, PropertyMock

from rich.table import Table

from alpaca_stream_cli.connection_monitor import ConnectionStatus
from alpaca_stream_cli.status_bar import (
    _fmt_latency,
    _fmt_uptime,
    _status_color,
    build_status_bar,
)


# ---------------------------------------------------------------------------
# _status_color
# ---------------------------------------------------------------------------

def test_status_color_connected():
    assert _status_color(ConnectionStatus.CONNECTED) == "green"


def test_status_color_disconnected():
    assert _status_color(ConnectionStatus.DISCONNECTED) == "red"


def test_status_color_reconnecting():
    assert _status_color(ConnectionStatus.RECONNECTING) == "yellow"


# ---------------------------------------------------------------------------
# _fmt_uptime
# ---------------------------------------------------------------------------

def test_fmt_uptime_none_returns_dashes():
    assert _fmt_uptime(None) == "--"


def test_fmt_uptime_zero():
    assert _fmt_uptime(0) == "00:00:00"


def test_fmt_uptime_one_hour():
    assert _fmt_uptime(3661) == "01:01:01"


def test_fmt_uptime_large():
    assert _fmt_uptime(7322) == "02:02:02"


# ---------------------------------------------------------------------------
# _fmt_latency
# ---------------------------------------------------------------------------

def _make_tracker(symbols=None, avg_map=None):
    tracker = MagicMock()
    tracker.symbols.return_value = symbols or []
    avg_map = avg_map or {}
    tracker.average_ms.side_effect = lambda s: avg_map.get(s.upper())
    return tracker


def test_fmt_latency_no_symbols_returns_dashes():
    tracker = _make_tracker()
    assert _fmt_latency(tracker) == "--"


def test_fmt_latency_single_symbol():
    tracker = _make_tracker(symbols=["AAPL"], avg_map={"AAPL": 12.5})
    result = _fmt_latency(tracker)
    assert result == "12.5ms"


def test_fmt_latency_multiple_symbols_averages():
    tracker = _make_tracker(
        symbols=["AAPL", "TSLA"],
        avg_map={"AAPL": 10.0, "TSLA": 20.0},
    )
    result = _fmt_latency(tracker)
    assert result == "15.0ms"


def test_fmt_latency_symbol_specific():
    tracker = _make_tracker(symbols=["AAPL"], avg_map={"AAPL": 8.3})
    result = _fmt_latency(tracker, symbol="AAPL")
    assert result == "8.3ms"


def test_fmt_latency_symbol_none_returns_dashes():
    tracker = _make_tracker(symbols=["AAPL"], avg_map={})
    result = _fmt_latency(tracker, symbol="AAPL")
    assert result == "--"


# ---------------------------------------------------------------------------
# build_status_bar
# ---------------------------------------------------------------------------

def _make_monitor(status=ConnectionStatus.CONNECTED, uptime=120.0, reconnects=0):
    monitor = MagicMock()
    type(monitor).status = PropertyMock(return_value=status)
    type(monitor).uptime_seconds = PropertyMock(return_value=uptime)
    type(monitor).reconnect_count = PropertyMock(return_value=reconnects)
    return monitor


def test_build_status_bar_returns_table():
    monitor = _make_monitor()
    tracker = _make_tracker()
    result = build_status_bar(monitor, tracker)
    assert isinstance(result, Table)


def test_build_status_bar_disconnected():
    monitor = _make_monitor(status=ConnectionStatus.DISCONNECTED, uptime=None)
    tracker = _make_tracker()
    result = build_status_bar(monitor, tracker, symbol_count=3, alert_count=1)
    assert isinstance(result, Table)
