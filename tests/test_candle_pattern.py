"""Tests for candle_pattern module."""
from __future__ import annotations
import pytest
from unittest.mock import MagicMock
from alpaca_stream_cli.candle_pattern import (
    detect_pattern,
    CandlePatternTracker,
    PatternResult,
)
from alpaca_stream_cli.ohlcv_bar import OHLCVBar


def _bar(symbol: str, o: float, h: float, l: float, c: float) -> OHLCVBar:
    bar = MagicMock(spec=OHLCVBar)
    bar.symbol = symbol
    bar.open = o
    bar.high = h
    bar.low = l
    bar.close = c
    return bar


def test_doji_detected():
    bar = _bar("AAPL", 100.0, 102.0, 98.0, 100.05)
    result = detect_pattern(bar)
    assert result.pattern == "doji"
    assert result.bullish is None


def test_hammer_detected():
    # Small body at top, long lower wick
    bar = _bar("TSLA", 110.0, 110.5, 100.0, 110.3)
    result = detect_pattern(bar)
    assert result.pattern == "hammer"
    assert result.bullish is True


def test_shooting_star_detected():
    # Small body at bottom, long upper wick
    bar = _bar("MSFT", 100.0, 110.0, 99.5, 100.3)
    result = detect_pattern(bar)
    assert result.pattern == "shooting_star"
    assert result.bullish is False


def test_bullish_marubozu_detected():
    bar = _bar("GOOG", 100.0, 110.0, 99.9, 109.9)
    result = detect_pattern(bar)
    assert result.pattern == "marubozu"
    assert result.bullish is True


def test_bearish_marubozu_detected():
    bar = _bar("AMZN", 110.0, 110.1, 100.0, 100.1)
    result = detect_pattern(bar)
    assert result.pattern == "marubozu"
    assert result.bullish is False


def test_zero_range_returns_none():
    bar = _bar("SPY", 100.0, 100.0, 100.0, 100.0)
    result = detect_pattern(bar)
    assert result.pattern is None
    assert result.bullish is None


def test_tracker_record_and_get():
    tracker = CandlePatternTracker()
    bar = _bar("AAPL", 100.0, 110.0, 99.9, 109.9)
    result = tracker.record(bar)
    assert isinstance(result, PatternResult)
    assert tracker.get("AAPL") is result


def test_tracker_normalizes_symbol_to_uppercase():
    tracker = CandlePatternTracker()
    bar = _bar("aapl", 100.0, 110.0, 99.9, 109.9)
    tracker.record(bar)
    assert tracker.get("AAPL") is not None
    assert tracker.get("aapl") is not None


def test_tracker_get_unknown_returns_none():
    tracker = CandlePatternTracker()
    assert tracker.get("UNKNOWN") is None


def test_tracker_all_results():
    tracker = CandlePatternTracker()
    for sym in ["AAPL", "TSLA", "MSFT"]:
        tracker.record(_bar(sym, 100.0, 110.0, 99.9, 109.9))
    results = tracker.all_results()
    assert len(results) == 3


def test_pattern_result_str_no_pattern():
    r = PatternResult(symbol="AAPL", pattern=None, bullish=None)
    assert "no pattern" in str(r)


def test_pattern_result_str_with_pattern():
    r = PatternResult(symbol="TSLA", pattern="hammer", bullish=True)
    assert "hammer" in str(r)
    assert "bullish" in str(r)
