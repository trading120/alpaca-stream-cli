"""Tests for OrderFlowIntegration."""
import pytest
from alpaca_stream_cli.order_flow_integration import OrderFlowIntegration


@pytest.fixture
def integration() -> OrderFlowIntegration:
    return OrderFlowIntegration(window=20)


def test_on_trade_returns_result(integration):
    result = integration.on_trade("AAPL", 150.0, 100)
    assert result is not None
    assert result.symbol == "AAPL"


def test_no_mid_defaults_to_buy(integration):
    result = integration.on_trade("AAPL", 150.0, 200)
    assert result.buy_volume == 200
    assert result.sell_volume == 0


def test_price_above_mid_is_buy(integration):
    integration.on_quote("MSFT", bid=299.0, ask=301.0)  # mid=300
    result = integration.on_trade("MSFT", 300.5, 100)
    assert result.buy_volume == 100
    assert result.sell_volume == 0


def test_price_below_mid_is_sell(integration):
    integration.on_quote("MSFT", bid=299.0, ask=301.0)  # mid=300
    result = integration.on_trade("MSFT", 299.0, 100)
    assert result.sell_volume == 100
    assert result.buy_volume == 0


def test_quote_normalizes_symbol(integration):
    integration.on_quote("tsla", bid=199.0, ask=201.0)
    result = integration.on_trade("TSLA", 200.5, 50)
    assert result is not None
    assert result.buy_volume == 50


def test_on_quote_invalid_bid_ignored(integration):
    integration.on_quote("NVDA", bid=0.0, ask=400.0)
    # mid should not be set; trade defaults to buy
    result = integration.on_trade("NVDA", 399.0, 10)
    assert result.buy_volume == 10


def test_get_returns_none_before_trades(integration):
    assert integration.get("AAPL") is None


def test_get_returns_result_after_trade(integration):
    integration.on_trade("AMD", 100.0, 50)
    assert integration.get("AMD") is not None


def test_symbols_tracks_seen_symbols(integration):
    integration.on_trade("A", 10.0, 1)
    integration.on_trade("B", 20.0, 2)
    assert set(integration.symbols()) == {"A", "B"}


def test_mixed_trades_produce_nonzero_ofi(integration):
    integration.on_quote("GOOG", bid=99.0, ask=101.0)  # mid=100
    integration.on_trade("GOOG", 101.0, 300)  # buy
    integration.on_trade("GOOG", 99.0, 100)   # sell
    result = integration.get("GOOG")
    assert result is not None
    assert result.ofi == pytest.approx(0.5)    # (300-100)/400
