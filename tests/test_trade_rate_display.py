"""Tests for alpaca_stream_cli.trade_rate_display."""
from datetime import datetime, timezone, timedelta

from rich.table import Table
from rich.text import Text

import pytest

from alpaca_stream_cli.trade_rate import TradeRateTracker
from alpaca_stream_cli.trade_rate_display import (
    _rate_color,
    _fmt_rate,
    build_trade_rate_table,
)


def _ts(offset: float = 0.0) -> datetime:
    return datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc) + timedelta(seconds=offset)


# --- _rate_color ---

def test_rate_color_zero_is_dim():
    assert _rate_color(0.0) == "dim white"


def test_rate_color_low_is_green():
    assert _rate_color(0.5) == "green"


def test_rate_color_medium_is_yellow():
    assert _rate_color(3.0) == "yellow"


def test_rate_color_high_is_red():
    assert _rate_color(10.0) == "bright_red"


# --- _fmt_rate ---

def test_fmt_rate_returns_text():
    result = _fmt_rate(1.5)
    assert isinstance(result, Text)


def test_fmt_rate_formats_two_decimals():
    result = _fmt_rate(2.0)
    assert "2.00" in result.plain


# --- build_trade_rate_table ---

@pytest.fixture
def populated_tracker():
    t = TradeRateTracker(window_seconds=10.0)
    for i in range(3):
        t.record("AAPL", ts=_ts(i))
    t.record("TSLA", ts=_ts(0))
    return t


def test_build_table_returns_table(populated_tracker):
    tbl = build_trade_rate_table(populated_tracker)
    assert isinstance(tbl, Table)


def test_table_has_three_columns(populated_tracker):
    tbl = build_trade_rate_table(populated_tracker)
    assert len(tbl.columns) == 3


def test_table_row_count_matches_symbols(populated_tracker):
    tbl = build_trade_rate_table(populated_tracker)
    assert tbl.row_count == 2


def test_table_respects_symbols_filter(populated_tracker):
    tbl = build_trade_rate_table(populated_tracker, symbols=["AAPL"])
    assert tbl.row_count == 1


def test_table_empty_tracker_has_no_rows():
    t = TradeRateTracker()
    tbl = build_trade_rate_table(t)
    assert tbl.row_count == 0


def test_custom_title_is_set(populated_tracker):
    tbl = build_trade_rate_table(populated_tracker, title="My TPS")
    assert tbl.title == "My TPS"
