"""Tests for candle_pattern_display module."""
from __future__ import annotations
import pytest
from unittest.mock import MagicMock
from rich.table import Table
from alpaca_stream_cli.candle_pattern import CandlePatternTracker, PatternResult
from alpaca_stream_cli.candle_pattern_display import (
    _fmt_pattern,
    _fmt_direction,
    _pattern_color,
    build_candle_pattern_table,
)
from alpaca_stream_cli.ohlcv_bar import OHLCVBar


def _bar(symbol: str, o: float, h: float, l: float, c: float) -> OHLCVBar:
    bar = MagicMock(spec=OHLCVBar)
    bar.symbol = symbol
    bar.open, bar.high, bar.low, bar.close = o, h, l, c
    return bar


def test_fmt_pattern_none_returns_dash():
    result = PatternResult(symbol="AAPL", pattern=None, bullish=None)
    text = _fmt_pattern(result)
    assert "—" in text.plain


def test_fmt_pattern_hammer_returns_label():
    result = PatternResult(symbol="TSLA", pattern="hammer", bullish=True)
    text = _fmt_pattern(result)
    assert "Hammer" in text.plain


def test_fmt_direction_bullish():
    result = PatternResult(symbol="AAPL", pattern="hammer", bullish=True)
    text = _fmt_direction(result)
    assert "Bullish" in text.plain


def test_fmt_direction_bearish():
    result = PatternResult(symbol="AAPL", pattern="shooting_star", bullish=False)
    text = _fmt_direction(result)
    assert "Bearish" in text.plain


def test_fmt_direction_none_returns_dash():
    result = PatternResult(symbol="AAPL", pattern="doji", bullish=None)
    text = _fmt_direction(result)
    assert "—" in text.plain


def test_pattern_color_bullish_is_green():
    result = PatternResult(symbol="AAPL", pattern="hammer", bullish=True)
    assert _pattern_color(result) == "green"


def test_pattern_color_bearish_is_red():
    result = PatternResult(symbol="AAPL", pattern="shooting_star", bullish=False)
    assert _pattern_color(result) == "red"


def test_pattern_color_neutral_is_yellow():
    result = PatternResult(symbol="AAPL", pattern="doji", bullish=None)
    assert _pattern_color(result) == "yellow"


def test_pattern_color_no_pattern_is_dim():
    result = PatternResult(symbol="AAPL", pattern=None, bullish=None)
    assert _pattern_color(result) == "dim"


def test_build_candle_pattern_table_returns_table():
    tracker = CandlePatternTracker()
    tracker.record(_bar("AAPL", 100.0, 110.0, 99.9, 109.9))
    table = build_candle_pattern_table(tracker, ["AAPL"])
    assert isinstance(table, Table)


def test_table_has_three_columns():
    tracker = CandlePatternTracker()
    table = build_candle_pattern_table(tracker, [])
    assert len(table.columns) == 3


def test_table_row_count_matches_symbols():
    tracker = CandlePatternTracker()
    for sym in ["AAPL", "TSLA", "MSFT"]:
        tracker.record(_bar(sym, 100.0, 110.0, 99.9, 109.9))
    table = build_candle_pattern_table(tracker, ["AAPL", "TSLA", "MSFT"])
    assert table.row_count == 3


def test_unknown_symbol_renders_placeholder():
    tracker = CandlePatternTracker()
    table = build_candle_pattern_table(tracker, ["UNKNOWN"])
    assert table.row_count == 1
