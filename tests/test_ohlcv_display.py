"""Tests for OHLCV display helpers."""
from datetime import datetime, timezone

import pytest
from rich.table import Table

from alpaca_stream_cli.ohlcv_bar import OHLCVBar
from alpaca_stream_cli.ohlcv_display import build_ohlcv_table, _change_color, _fmt_change


def _bar(symbol="AAPL", open=100.0, high=110.0, low=95.0, close=105.0, volume=5000.0):
    return OHLCVBar(
        symbol=symbol,
        open=open, high=high, low=low, close=close,
        volume=volume,
        bar_time=datetime(2024, 1, 1, 9, 30, tzinfo=timezone.utc),
    )


def test_build_ohlcv_table_returns_table():
    table = build_ohlcv_table([_bar()])
    assert isinstance(table, Table)


def test_table_has_eight_columns():
    table = build_ohlcv_table([_bar()])
    assert len(table.columns) == 8


def test_table_row_count_matches_bars():
    bars = [_bar("AAPL"), _bar("MSFT"), _bar("TSLA")]
    table = build_ohlcv_table(bars)
    assert table.row_count == 3


def test_empty_bars_produces_empty_table():
    table = build_ohlcv_table([])
    assert table.row_count == 0


def test_change_color_positive():
    assert _change_color(2.5) == "green"


def test_change_color_negative():
    assert _change_color(-1.0) == "red"


def test_change_color_zero():
    assert _change_color(0.0) == "white"


def test_change_color_none():
    assert _change_color(None) == "dim"


def test_fmt_change_positive_has_plus():
    bar = _bar(open=100.0, close=110.0)
    result = _fmt_change(bar)
    assert "+" in result


def test_fmt_change_negative_no_plus():
    bar = _bar(open=110.0, close=100.0)
    result = _fmt_change(bar)
    assert result.count("+") == 0


def test_custom_title_applied():
    table = build_ohlcv_table([], title="My Bars")
    assert table.title == "My Bars"
