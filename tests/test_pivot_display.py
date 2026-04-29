"""Tests for pivot_display.build_pivot_table."""
import pytest
from rich.table import Table

from alpaca_stream_cli.pivot_points import PivotPointTracker
from alpaca_stream_cli.pivot_display import build_pivot_table, _level_color


@pytest.fixture
def tracker() -> PivotPointTracker:
    t = PivotPointTracker()
    t.update("AAPL", 150.0, 140.0, 148.0)
    t.update("TSLA", 700.0, 680.0, 695.0)
    return t


def test_build_pivot_table_returns_table(tracker):
    table = build_pivot_table(tracker, ["AAPL", "TSLA"])
    assert isinstance(table, Table)


def test_table_has_eight_columns(tracker):
    table = build_pivot_table(tracker, ["AAPL"])
    assert len(table.columns) == 8


def test_table_row_count_matches_symbols(tracker):
    table = build_pivot_table(tracker, ["AAPL", "TSLA"])
    assert table.row_count == 2


def test_unknown_symbol_renders_placeholder(tracker):
    table = build_pivot_table(tracker, ["UNKNOWN"])
    assert table.row_count == 1


def test_empty_symbols_produces_empty_table(tracker):
    table = build_pivot_table(tracker, [])
    assert table.row_count == 0


def test_level_color_near_price_is_yellow():
    color = _level_color(price=100.0, level=100.3, tolerance=0.005)
    assert "yellow" in color


def test_level_color_above_price_is_green():
    color = _level_color(price=100.0, level=110.0)
    assert color == "green"


def test_level_color_below_price_is_red():
    color = _level_color(price=100.0, level=90.0)
    assert color == "red"


def test_level_color_zero_price_returns_white():
    color = _level_color(price=0.0, level=50.0)
    assert color == "white"


def test_table_with_current_prices(tracker):
    prices = {"AAPL": 145.0, "TSLA": 690.0}
    table = build_pivot_table(tracker, ["AAPL", "TSLA"], current_prices=prices)
    assert table.row_count == 2
