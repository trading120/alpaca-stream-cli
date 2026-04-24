"""Tests for imbalance_display module."""
import pytest
from rich.table import Table
from alpaca_stream_cli.bid_ask_imbalance import BidAskImbalanceTracker
from alpaca_stream_cli.imbalance_display import (
    _imbalance_bar,
    _imbalance_color,
    _fmt_imbalance,
    build_imbalance_table,
)


def test_fmt_imbalance_none_returns_dashes():
    assert _fmt_imbalance(None) == "--"


def test_fmt_imbalance_positive_has_plus():
    result = _fmt_imbalance(0.5)
    assert result.startswith("+")


def test_fmt_imbalance_negative_has_minus():
    result = _fmt_imbalance(-0.5)
    assert result.startswith("-")


def test_fmt_imbalance_zero_has_plus():
    result = _fmt_imbalance(0.0)
    assert result.startswith("+")


def test_imbalance_color_strong_positive_is_green():
    assert _imbalance_color(0.5) == "green"


def test_imbalance_color_strong_negative_is_red():
    assert _imbalance_color(-0.5) == "red"


def test_imbalance_color_neutral_is_yellow():
    assert _imbalance_color(0.1) == "yellow"


def test_imbalance_color_none_is_dim():
    assert _imbalance_color(None) == "dim"


def test_imbalance_bar_returns_string():
    result = _imbalance_bar(0.5)
    assert isinstance(result, str)
    assert "█" in result


def test_imbalance_bar_zero_has_no_filled():
    result = _imbalance_bar(0.0)
    assert "░" in result


def test_build_imbalance_table_returns_table():
    tracker = BidAskImbalanceTracker()
    tracker.record("AAPL", 100, 50)
    table = build_imbalance_table(tracker, ["AAPL"])
    assert isinstance(table, Table)


def test_build_imbalance_table_has_four_columns():
    tracker = BidAskImbalanceTracker()
    table = build_imbalance_table(tracker, [])
    assert len(table.columns) == 4


def test_build_imbalance_table_row_count_matches_symbols():
    tracker = BidAskImbalanceTracker()
    tracker.record("AAPL", 100, 50)
    tracker.record("MSFT", 200, 80)
    table = build_imbalance_table(tracker, ["AAPL", "MSFT"])
    assert table.row_count == 2


def test_build_imbalance_table_unknown_symbol_renders():
    tracker = BidAskImbalanceTracker()
    table = build_imbalance_table(tracker, ["UNKNOWN"])
    assert table.row_count == 1
