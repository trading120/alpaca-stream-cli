"""Tests for alpaca_stream_cli.news_sentiment."""
import pytest
from alpaca_stream_cli.news_sentiment import (
    SentimentTracker,
    SymbolSentiment,
    _label,
)


def test_label_bullish():
    assert _label(0.5) == "Bullish"
    assert _label(0.4) == "Bullish"


def test_label_bearish():
    assert _label(-0.5) == "Bearish"
    assert _label(-0.4) == "Bearish"


def test_label_neutral():
    assert _label(0.0) == "Neutral"
    assert _label(0.2) == "Neutral"
    assert _label(-0.2) == "Neutral"


def test_invalid_weights_raise():
    with pytest.raises(ValueError):
        SymbolSentiment(roc_weight=0.5, rate_weight=0.3)


def test_result_before_update_is_neutral():
    sym = SymbolSentiment()
    r = sym.result("AAPL")
    assert r.score == 0.0
    assert r.label == "Neutral"
    assert r.symbol == "AAPL"


def test_positive_roc_pushes_score_positive():
    sym = SymbolSentiment()
    sym.update(roc=2.0, trade_rate=None)
    r = sym.result("AAPL")
    assert r.score > 0


def test_negative_roc_pushes_score_negative():
    sym = SymbolSentiment()
    sym.update(roc=-2.0, trade_rate=None)
    r = sym.result("AAPL")
    assert r.score < 0


def test_score_clamped_to_minus_one():
    sym = SymbolSentiment()
    sym.update(roc=-100.0, trade_rate=0.0)
    r = sym.result("AAPL")
    assert r.score >= -1.0


def test_score_clamped_to_plus_one():
    sym = SymbolSentiment()
    sym.update(roc=100.0, trade_rate=100.0)
    r = sym.result("AAPL")
    assert r.score <= 1.0


def test_tracker_normalizes_symbol_to_uppercase():
    tracker = SentimentTracker()
    tracker.update("aapl", roc=1.0, trade_rate=2.0)
    r = tracker.get("AAPL")
    assert r is not None
    assert r.symbol == "AAPL"


def test_tracker_get_unknown_returns_none():
    tracker = SentimentTracker()
    assert tracker.get("UNKNOWN") is None


def test_tracker_all_results_includes_all_symbols():
    tracker = SentimentTracker()
    tracker.update("AAPL", 1.0, 2.0)
    tracker.update("TSLA", -1.0, 0.5)
    results = tracker.all_results()
    assert "AAPL" in results
    assert "TSLA" in results


def test_tracker_remove_symbol():
    tracker = SentimentTracker()
    tracker.update("AAPL", 1.0, 2.0)
    tracker.remove("AAPL")
    assert tracker.get("AAPL") is None


def test_tracker_update_returns_result():
    tracker = SentimentTracker()
    r = tracker.update("MSFT", roc=0.5, trade_rate=1.5)
    assert r.symbol == "MSFT"
    assert isinstance(r.score, float)
