"""Tests for momentum_display helpers."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest
from rich.table import Table

from alpaca_stream_cli.momentum_tracker import MomentumTracker
from alpaca_stream_cli.momentum_display import (
    _roc_color,
    _arrow,
    _fmt_roc,
    build_momentum_table,
)


def _ts(offset: float = 0.0) -> datetime:
    return datetime.fromtimestamp(1_700_000_000 + offset, tz=timezone.utc)


# --- _roc_color ---

def test_roc_color_none_is_dim():
    assert _roc_color(None) == "dim"


def test_roc_color_strong_positive_is_bold_green():
    assert _roc_color(3.0) == "bold green"


def test_roc_color_mild_positive_is_green():
    assert _roc_color(1.0) == "green"


def test_roc_color_flat_is_white():
    assert _roc_color(0.0) == "white"


def test_roc_color_mild_negative_is_red():
    assert _roc_color(-1.0) == "red"


def test_roc_color_strong_negative_is_bold_red():
    assert _roc_color(-3.0) == "bold red"


# --- _arrow ---

def test_arrow_none_returns_dash():
    assert _arrow(None) == "-"


def test_arrow_positive_returns_up():
    assert _arrow(1.0) == "▲"


def test_arrow_negative_returns_down():
    assert _arrow(-1.0) == "▼"


def test_arrow_flat_returns_dot():
    assert _arrow(0.0) == "●"


# --- _fmt_roc ---

def test_fmt_roc_none_returns_dashes():
    assert _fmt_roc(None) == "--"


def test_fmt_roc_positive_has_plus():
    result = _fmt_roc(2.5)
    assert result.startswith("+")


def test_fmt_roc_negative_no_plus():
    result = _fmt_roc(-1.5)
    assert not result.startswith("+")
    assert "-" in result


def test_fmt_roc_two_decimal_places():
    assert _fmt_roc(1.0) == "+1.00%"


# --- build_momentum_table ---

@pytest.fixture
def populated_tracker() -> MomentumTracker:
    t = MomentumTracker(window_seconds=60)
    t.record("AAPL", 150.0, _ts(0))
    t.record("AAPL", 153.0, _ts(10))
    t.record("MSFT", 300.0, _ts(0))
    t.record("MSFT", 295.0, _ts(10))
    return t


def test_build_momentum_table_returns_table(populated_tracker):
    tbl = build_momentum_table(populated_tracker, ["AAPL", "MSFT"])
    assert isinstance(tbl, Table)


def test_table_has_five_columns(populated_tracker):
    tbl = build_momentum_table(populated_tracker, ["AAPL", "MSFT"])
    assert len(tbl.columns) == 5


def test_table_row_count_matches_symbols(populated_tracker):
    tbl = build_momentum_table(populated_tracker, ["AAPL", "MSFT"])
    assert tbl.row_count == 2


def test_unknown_symbol_renders_placeholder(populated_tracker):
    tbl = build_momentum_table(populated_tracker, ["UNKNOWN"])
    assert tbl.row_count == 1


def test_empty_symbols_produces_empty_table(populated_tracker):
    tbl = build_momentum_table(populated_tracker, [])
    assert tbl.row_count == 0
