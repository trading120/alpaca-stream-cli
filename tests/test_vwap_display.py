"""Tests for VWAP display table builder."""
import pytest
from rich.table import Table
from alpaca_stream_cli.vwap_tracker import VWAPTracker
from alpaca_stream_cli.vwap_display import (
    build_vwap_table,
    _deviation_color,
    _fmt_deviation,
)


def _make_tracker(*records) -> VWAPTracker:
    """Helper: create a tracker with (symbol, price, volume) records."""
    t = VWAPTracker()
    for sym, price, vol in records:
        t.record(sym, price, vol)
    return t


def test_build_vwap_table_returns_table():
    t = _make_tracker(("AAPL", 150.0, 100))
    result = build_vwap_table(["AAPL"], t, {"AAPL": 151.0})
    assert isinstance(result, Table)


def test_table_has_five_columns():
    t = _make_tracker(("AAPL", 150.0, 100))
    table = build_vwap_table(["AAPL"], t, {"AAPL": 150.0})
    assert len(table.columns) == 5


def test_table_row_count_matches_symbols():
    t = _make_tracker(("AAPL", 150.0, 100), ("MSFT", 300.0, 50))
    table = build_vwap_table(["AAPL", "MSFT"], t, {})
    assert table.row_count == 2


def test_empty_symbols_produces_empty_table():
    t = VWAPTracker()
    table = build_vwap_table([], t, {})
    assert table.row_count == 0


def test_deviation_color_above_threshold_is_green():
    assert _deviation_color(101.0, 100.0) == "green"


def test_deviation_color_below_threshold_is_red():
    assert _deviation_color(99.0, 100.0) == "red"


def test_deviation_color_within_threshold_is_yellow():
    assert _deviation_color(100.1, 100.0) == "yellow"


def test_deviation_color_none_price_is_white():
    assert _deviation_color(None, 100.0) == "white"


def test_deviation_color_none_vwap_is_white():
    assert _deviation_color(100.0, None) == "white"


def test_fmt_deviation_positive_has_plus():
    result = _fmt_deviation(102.0, 100.0)
    assert result.startswith("+")


def test_fmt_deviation_negative_has_minus():
    result = _fmt_deviation(98.0, 100.0)
    assert result.startswith("-")


def test_fmt_deviation_none_returns_dashes():
    assert _fmt_deviation(None, 100.0) == "--"
    assert _fmt_deviation(100.0, None) == "--"


def test_fmt_deviation_exact_match_is_zero():
    result = _fmt_deviation(100.0, 100.0)
    assert "0.00%" in result
