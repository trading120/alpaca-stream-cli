"""Tests for price_velocity_display module."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from rich.table import Table
from rich.text import Text

from alpaca_stream_cli.price_change_tracker import PriceChangeTracker
from alpaca_stream_cli.price_velocity_display import _arrow, _fmt_pct, build_velocity_table


# ---------------------------------------------------------------------------
# _arrow
# ---------------------------------------------------------------------------

def test_arrow_none_returns_dash():
    result = _arrow(None)
    assert isinstance(result, Text)
    assert "—" in result.plain


def test_arrow_strong_positive():
    result = _arrow(1.0)
    assert "▲▲" in result.plain
    assert result.style == "bold green"


def test_arrow_weak_positive():
    result = _arrow(0.1)
    assert "▲" in result.plain
    assert result.style == "green"


def test_arrow_strong_negative():
    result = _arrow(-1.0)
    assert "▼▼" in result.plain
    assert result.style == "bold red"


def test_arrow_weak_negative():
    result = _arrow(-0.1)
    assert "▼" in result.plain
    assert result.style == "red"


def test_arrow_zero_returns_dash():
    result = _arrow(0.0)
    assert "—" in result.plain


# ---------------------------------------------------------------------------
# _fmt_pct
# ---------------------------------------------------------------------------

def test_fmt_pct_none_returns_dash():
    result = _fmt_pct(None)
    assert "—" in result.plain


def test_fmt_pct_positive_has_content():
    result = _fmt_pct(2.5)
    assert result.plain != ""


def test_fmt_pct_negative_has_content():
    result = _fmt_pct(-1.3)
    assert result.plain != ""


# ---------------------------------------------------------------------------
# build_velocity_table
# ---------------------------------------------------------------------------

@pytest.fixture()
def tracker():
    return PriceChangeTracker()


def _ts(offset: float = 0.0) -> datetime:
    from datetime import timedelta
    return datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc) + timedelta(seconds=offset)


def test_build_velocity_table_returns_table(tracker):
    table = build_velocity_table(["AAPL", "MSFT"], tracker)
    assert isinstance(table, Table)


def test_table_has_five_columns(tracker):
    table = build_velocity_table(["AAPL"], tracker)
    assert len(table.columns) == 5


def test_table_row_count_matches_symbols(tracker):
    symbols = ["AAPL", "MSFT", "GOOG"]
    table = build_velocity_table(symbols, tracker)
    assert table.row_count == len(symbols)


def test_table_with_recorded_prices(tracker):
    tracker.record("AAPL", 150.0, _ts(0))
    tracker.record("AAPL", 151.5, _ts(30))
    table = build_velocity_table(["AAPL"], tracker, window_seconds=60.0)
    assert table.row_count == 1


def test_table_normalizes_symbol_case(tracker):
    tracker.record("aapl", 150.0, _ts(0))
    table = build_velocity_table(["aapl"], tracker)
    # Should not raise and should produce one row
    assert table.row_count == 1


def test_table_custom_title(tracker):
    table = build_velocity_table(["TSLA"], tracker, title="Custom Title")
    assert table.title == "Custom Title"
