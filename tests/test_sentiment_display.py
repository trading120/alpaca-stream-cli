"""Tests for alpaca_stream_cli.sentiment_display."""
import pytest
from rich.table import Table

from alpaca_stream_cli.news_sentiment import SentimentResult, SentimentTracker
from alpaca_stream_cli.sentiment_display import (
    _score_color,
    _label_color,
    _fmt_score,
    build_sentiment_table,
)


def _result(symbol: str, score: float, label: str) -> SentimentResult:
    return SentimentResult(symbol=symbol, score=score, label=label, roc=None, trade_rate=None)


def test_score_color_strong_positive_is_bold_green():
    assert _score_color(0.5) == "bold green"


def test_score_color_mild_positive_is_green():
    assert _score_color(0.2) == "green"


def test_score_color_neutral_is_white():
    assert _score_color(0.0) == "white"


def test_score_color_mild_negative_is_red():
    assert _score_color(-0.2) == "red"


def test_score_color_strong_negative_is_bold_red():
    assert _score_color(-0.5) == "bold red"


def test_label_color_bullish_is_green():
    assert _label_color("Bullish") == "green"


def test_label_color_bearish_is_red():
    assert _label_color("Bearish") == "red"


def test_label_color_neutral_is_white():
    assert _label_color("Neutral") == "white"


def test_fmt_score_positive_has_plus():
    assert _fmt_score(0.5).startswith("+")


def test_fmt_score_negative_has_minus():
    assert _fmt_score(-0.5).startswith("-")


def test_build_sentiment_table_returns_table():
    results = {"AAPL": _result("AAPL", 0.5, "Bullish")}
    t = build_sentiment_table(results)
    assert isinstance(t, Table)


def test_table_has_five_columns():
    results = {"AAPL": _result("AAPL", 0.0, "Neutral")}
    t = build_sentiment_table(results)
    assert len(t.columns) == 5


def test_table_row_count_matches_results():
    results = {
        "AAPL": _result("AAPL", 0.3, "Neutral"),
        "TSLA": _result("TSLA", -0.6, "Bearish"),
        "MSFT": _result("MSFT", 0.7, "Bullish"),
    }
    t = build_sentiment_table(results)
    assert t.row_count == 3


def test_empty_results_produces_empty_table():
    t = build_sentiment_table({})
    assert t.row_count == 0


def test_table_title_is_configurable():
    t = build_sentiment_table({}, title="Custom Title")
    assert t.title == "Custom Title"


def test_tracker_integration_with_display():
    tracker = SentimentTracker()
    tracker.update("AAPL", roc=1.5, trade_rate=3.0)
    tracker.update("GOOG", roc=-0.5, trade_rate=0.8)
    results = tracker.all_results()
    t = build_sentiment_table(results)
    assert t.row_count == 2
