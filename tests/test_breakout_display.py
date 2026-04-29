"""Tests for breakout_display module."""
import pytest
from rich.table import Table
from alpaca_stream_cli.breakout_tracker import BreakoutTracker
from alpaca_stream_cli.breakout_display import (
    build_breakout_table,
    _breakout_color,
    _fmt_price,
    _fmt_pct,
)
from alpaca_stream_cli.breakout_tracker import BreakoutResult


@pytest.fixture
def tracker():
    t = BreakoutTracker(window=4, max_symbols=10)
    for p in [100.0, 102.0, 98.0, 101.0]:
        t.record("AAPL", p)
    for p in [200.0, 205.0, 195.0, 202.0]:
        t.record("TSLA", p)
    return t


def test_build_breakout_table_returns_table(tracker):
    table = build_breakout_table(tracker, ["AAPL", "TSLA"])
    assert isinstance(table, Table)


def test_table_has_six_columns(tracker):
    table = build_breakout_table(tracker, ["AAPL"])
    assert len(table.columns) == 6


def test_table_row_count_matches_symbols(tracker):
    table = build_breakout_table(tracker, ["AAPL", "TSLA"])
    assert table.row_count == 2


def test_unknown_symbol_renders_placeholder(tracker):
    table = build_breakout_table(tracker, ["UNKNOWN"])
    assert table.row_count == 1


def test_empty_symbols_produces_empty_table(tracker):
    table = build_breakout_table(tracker, [])
    assert table.row_count == 0


def test_fmt_price_formats_correctly():
    assert _fmt_price(1234.5) == "$1,234.50"


def test_fmt_pct_none_returns_dash():
    assert _fmt_pct(None) == "—"


def test_fmt_pct_positive_has_plus():
    result = _fmt_pct(3.14)
    assert "+" in result
    assert "3.14" in result


def test_fmt_pct_negative_has_minus():
    result = _fmt_pct(-2.5)
    assert "-" in result


def test_breakout_color_up_is_green():
    r = BreakoutResult(
        symbol="X", price=110.0, upper=105.0, lower=95.0,
        breakout_up=True, breakout_down=False,
        pct_above_upper=4.76, pct_below_lower=None,
    )
    assert "green" in _breakout_color(r)


def test_breakout_color_down_is_red():
    r = BreakoutResult(
        symbol="X", price=90.0, upper=105.0, lower=95.0,
        breakout_up=False, breakout_down=True,
        pct_above_upper=None, pct_below_lower=-5.0,
    )
    assert "red" in _breakout_color(r)


def test_breakout_color_range_is_white():
    r = BreakoutResult(
        symbol="X", price=100.0, upper=105.0, lower=95.0,
        breakout_up=False, breakout_down=False,
        pct_above_upper=None, pct_below_lower=None,
    )
    assert _breakout_color(r) == "white"
