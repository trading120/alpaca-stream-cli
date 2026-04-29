"""Tests for FundingRateTracker and FundingRateResult."""
import pytest
from alpaca_stream_cli.funding_rate import FundingRateTracker, FundingRateResult


def test_invalid_window_raises():
    with pytest.raises(ValueError):
        FundingRateTracker(window=1)


def test_invalid_max_symbols_raises():
    with pytest.raises(ValueError):
        FundingRateTracker(max_symbols=0)


def test_get_before_any_record_returns_none():
    t = FundingRateTracker()
    assert t.get("AAPL") is None


def test_record_normalizes_symbol_to_uppercase():
    t = FundingRateTracker()
    result = t.record("aapl", 150.0, 150.1)
    assert result is not None
    assert result.symbol == "AAPL"


def test_single_record_returns_result():
    t = FundingRateTracker()
    r = t.record("AAPL", 150.05, 150.0)
    assert isinstance(r, FundingRateResult)
    assert r.sample_count == 1


def test_positive_deviation_gives_positive_rate():
    t = FundingRateTracker()
    r = t.record("TSLA", 205.0, 200.0)
    assert r is not None
    assert r.rate_pct > 0


def test_negative_deviation_gives_negative_rate():
    t = FundingRateTracker()
    r = t.record("TSLA", 195.0, 200.0)
    assert r is not None
    assert r.rate_pct < 0


def test_window_limits_samples():
    t = FundingRateTracker(window=3)
    for price in [100.0, 101.0, 102.0, 103.0, 104.0]:
        r = t.record("SPY", price, 100.0)
    assert r is not None
    assert r.sample_count == 3


def test_zero_mid_price_does_not_crash():
    t = FundingRateTracker()
    r = t.record("AAPL", 150.0, 0.0)
    assert r is None


def test_label_bullish():
    t = FundingRateTracker()
    # force large positive deviations
    for _ in range(5):
        t.record("AAPL", 110.0, 100.0)
    r = t.get("AAPL")
    assert r is not None
    assert r.label == "bullish"


def test_label_bearish():
    t = FundingRateTracker()
    for _ in range(5):
        t.record("AAPL", 90.0, 100.0)
    r = t.get("AAPL")
    assert r is not None
    assert r.label == "bearish"


def test_label_neutral():
    t = FundingRateTracker()
    t.record("AAPL", 100.001, 100.0)
    r = t.get("AAPL")
    assert r is not None
    assert r.label == "neutral"


def test_all_results_returns_only_recorded_symbols():
    t = FundingRateTracker()
    t.record("AAPL", 150.0, 149.9)
    t.record("MSFT", 300.0, 299.8)
    results = t.all_results()
    assert set(results.keys()) == {"AAPL", "MSFT"}


def test_max_symbols_cap():
    t = FundingRateTracker(max_symbols=2)
    t.record("A", 10.0, 10.0)
    t.record("B", 10.0, 10.0)
    r = t.record("C", 10.0, 10.0)
    assert r is None
