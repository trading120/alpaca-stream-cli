"""Tests for stats_display module."""

import pytest
from rich.table import Table

from alpaca_stream_cli.session_stats import SessionStats
from alpaca_stream_cli.stats_display import build_stats_table


@pytest.fixture
def populated_stats():
    s = SessionStats()
    s.update("AAPL", 150.0, 1000)
    s.update("AAPL", 155.0, 500)
    s.update("AAPL", 148.0, 200)
    s.update("MSFT", 300.0, 2000)
    return s


def test_build_stats_table_returns_table(populated_stats):
    table = build_stats_table(populated_stats, ["AAPL", "MSFT"])
    assert isinstance(table, Table)


def test_table_has_correct_column_count(populated_stats):
    table = build_stats_table(populated_stats, ["AAPL"])
    assert len(table.columns) == 8


def test_table_row_count_matches_symbols(populated_stats):
    table = build_stats_table(populated_stats, ["AAPL", "MSFT"])
    assert table.row_count == 2


def test_unknown_symbol_renders_placeholder(populated_stats):
    table = build_stats_table(populated_stats, ["TSLA"])
    assert table.row_count == 1


def test_empty_symbols_list_produces_empty_table(populated_stats):
    table = build_stats_table(populated_stats, [])
    assert table.row_count == 0


def test_table_title(populated_stats):
    table = build_stats_table(populated_stats, ["AAPL"])
    assert table.title == "Session Statistics"
