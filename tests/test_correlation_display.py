"""Tests for correlation_display helpers."""
import pytest
from rich.table import Table

from alpaca_stream_cli.correlation_tracker import CorrelationTracker, CorrelationResult
from alpaca_stream_cli.correlation_display import (
    _corr_color,
    _fmt_corr,
    _strength_label,
    build_correlation_table,
)


def _make_tracker_with_data():
    t = CorrelationTracker(window=5, max_symbols=10)
    prices = [100.0, 101.0, 102.0, 103.0, 104.0]
    for p in prices:
        t.record("AAPL", p)
        t.record("MSFT", p * 2)
        t.record("TSLA", 200.0 - p)
    return t


def test_fmt_corr_none_returns_dashes():
    assert _fmt_corr(None) == "--"


def test_fmt_corr_positive():
    assert _fmt_corr(0.856) == "+0.856"


def test_fmt_corr_negative():
    assert "-" in _fmt_corr(-0.5)


def test_corr_color_none_is_dim():
    assert _corr_color(None) == "dim"


def test_corr_color_strong_positive_is_bold_green():
    assert _corr_color(0.9) == "bold green"


def test_corr_color_mild_positive_is_green():
    assert _corr_color(0.5) == "green"


def test_corr_color_neutral_is_white():
    assert _corr_color(0.0) == "white"


def test_corr_color_mild_negative_is_red():
    assert _corr_color(-0.5) == "red"


def test_corr_color_strong_negative_is_bold_red():
    assert _corr_color(-0.9) == "bold red"


def test_strength_label_none_returns_dashes():
    assert _strength_label(None) == "--"


def test_strength_label_strong_positive():
    assert _strength_label(0.8) == "strong pos"


def test_strength_label_strong_negative():
    assert _strength_label(-0.8) == "strong neg"


def test_strength_label_neutral():
    assert _strength_label(0.1) == "neutral"


def test_build_correlation_table_returns_table():
    t = _make_tracker_with_data()
    table = build_correlation_table(t)
    assert isinstance(table, Table)


def test_table_has_five_columns():
    t = _make_tracker_with_data()
    table = build_correlation_table(t)
    assert len(table.columns) == 5


def test_table_row_count_matches_pairs():
    t = _make_tracker_with_data()
    pairs = t.pairs()
    table = build_correlation_table(t)
    assert table.row_count == len(pairs)


def test_empty_tracker_produces_empty_table():
    t = CorrelationTracker()
    table = build_correlation_table(t)
    assert table.row_count == 0


def test_max_rows_limits_output():
    t = _make_tracker_with_data()
    table = build_correlation_table(t, max_rows=1)
    assert table.row_count == 1


def test_explicit_pairs_respected():
    t = _make_tracker_with_data()
    table = build_correlation_table(t, pairs=[("AAPL", "MSFT")])
    assert table.row_count == 1
