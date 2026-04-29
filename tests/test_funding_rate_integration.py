"""Tests for FundingRateIntegration."""
import pytest
from alpaca_stream_cli.funding_rate_integration import FundingRateIntegration


def test_on_trade_without_quote_returns_none():
    integ = FundingRateIntegration()
    result = integ.on_trade("AAPL", 150.0)
    assert result is None


def test_on_quote_then_trade_returns_result():
    integ = FundingRateIntegration()
    integ.on_quote("AAPL", 149.9, 150.1)
    result = integ.on_trade("AAPL", 150.05)
    assert result is not None
    assert result.symbol == "AAPL"


def test_mid_price_computed_correctly():
    integ = FundingRateIntegration()
    integ.on_quote("AAPL", 100.0, 102.0)  # mid = 101.0
    result = integ.on_trade("AAPL", 101.0)
    assert result is not None
    # trade at mid => deviation near 0
    assert abs(result.rate_pct) < 0.01


def test_quote_normalizes_symbol():
    integ = FundingRateIntegration()
    integ.on_quote("aapl", 149.9, 150.1)
    result = integ.on_trade("AAPL", 150.05)
    assert result is not None


def test_trade_normalizes_symbol():
    integ = FundingRateIntegration()
    integ.on_quote("AAPL", 149.9, 150.1)
    result = integ.on_trade("aapl", 150.05)
    assert result is not None
    assert result.symbol == "AAPL"


def test_invalid_quote_bid_zero_ignored():
    integ = FundingRateIntegration()
    integ.on_quote("AAPL", 0.0, 150.1)
    result = integ.on_trade("AAPL", 150.0)
    assert result is None


def test_get_before_any_data_returns_none():
    integ = FundingRateIntegration()
    assert integ.get("AAPL") is None


def test_all_results_empty_initially():
    integ = FundingRateIntegration()
    assert integ.all_results() == {}


def test_all_results_after_trades():
    integ = FundingRateIntegration()
    integ.on_quote("AAPL", 149.9, 150.1)
    integ.on_quote("MSFT", 299.8, 300.2)
    integ.on_trade("AAPL", 150.0)
    integ.on_trade("MSFT", 300.0)
    results = integ.all_results()
    assert "AAPL" in results
    assert "MSFT" in results


def test_tracker_property_accessible():
    integ = FundingRateIntegration()
    from alpaca_stream_cli.funding_rate import FundingRateTracker
    assert isinstance(integ.tracker, FundingRateTracker)
