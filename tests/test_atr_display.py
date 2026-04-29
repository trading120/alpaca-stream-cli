"""Tests for ATR display helpers."""
from __future__ import annotations

import pytest
from rich.table import Table

from alpaca_stream_cli.atr_tracker import ATRTracker
from alpaca_stream_cli.atr_display import (
    _volatility_color,
    _fmt_atr,
    _fmt_pct,
    build_atr_table,
)


# ---------------------------------------------------------------------------
# _volatility_color
# ---------------------------------------------------------------------------

def test_volatility_color_none_atr_is_dim():
    assert _volatility_color(None, 100.0) == "dim"


def test_volatility_color_none_price_is_dim():
    assert _volatility_color(5.0, None) == "dim"


def test_volatility_color_zero_price_is_dim():
    assert _volatility_color(5.0, 0.0) == "dim"


def test_volatility_color_high_is_bold_red():
    # atr=10, price=100 => 10% >= 5%
    assert _volatility_color(10.0, 100.0) == "bold red"


def test_volatility_color_medium_is_yellow():
    # atr=3, price=100 => 3% in [2, 5)
    assert _volatility_color(3.0, 100.0) == "yellow"


def test_volatility_color_low_is_green():
    # atr=1, price=100 => 1% in [0.5, 2)
    assert _volatility_color(1.0, 100.0) == "green"


def test_volatility_color_flat_is_dim():
    # atr=0.1, price=100 => 0.1% < 0.5%
    assert _volatility_color(0.1, 100.0) == "dim"


# ---------------------------------------------------------------------------
# _fmt_atr
# ---------------------------------------------------------------------------

def test_fmt_atr_none_returns_dashes():
    assert "---" in _fmt_atr(None)


def test_fmt_atr_formats_four_decimals():
    result = _fmt_atr(3.14159)
    assert "3.1416" in result


# ---------------------------------------------------------------------------
# _fmt_pct
# ---------------------------------------------------------------------------

def test_fmt_pct_none_atr_returns_dashes():
    assert "---" in _fmt_pct(None, 100.0)


def test_fmt_pct_none_price_returns_dashes():
    assert "---" in _fmt_pct(5.0, None)


def test_fmt_pct_correct_value():
    result = _fmt_pct(2.0, 100.0)
    assert "2.00%" in result


# ---------------------------------------------------------------------------
# build_atr_table
# ---------------------------------------------------------------------------

def _make_tracker_with_data(period: int = 3) -> ATRTracker:
    t = ATRTracker(period=period)
    for sym in ["AAPL", "MSFT"]:
        t.record(sym, 150, 145, 148)
        t.record(sym, 152, 147, 150)
        t.record(sym, 155, 149, 153)
    return t


def test_build_atr_table_returns_table():
    tracker = _make_tracker_with_data()
    result = build_atr_table(tracker)
    assert isinstance(result, Table)


def test_table_has_five_columns():
    tracker = _make_tracker_with_data()
    result = build_atr_table(tracker)
    assert len(result.columns) == 5


def test_table_row_count_matches_symbols():
    tracker = _make_tracker_with_data()
    result = build_atr_table(tracker)
    assert result.row_count == 2


def test_empty_tracker_produces_empty_table():
    tracker = ATRTracker(period=3)
    result = build_atr_table(tracker)
    assert result.row_count == 0


def test_max_rows_limits_output():
    tracker = _make_tracker_with_data()
    result = build_atr_table(tracker, max_rows=1)
    assert result.row_count == 1


def test_prices_passed_to_table():
    tracker = _make_tracker_with_data()
    prices = {"AAPL": 150.0, "MSFT": 300.0}
    result = build_atr_table(tracker, prices=prices)
    assert isinstance(result, Table)
    assert result.row_count == 2
