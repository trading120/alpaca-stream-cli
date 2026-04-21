"""Tests for AlertDispatcher — throttled alert evaluation and dispatch."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from alpaca_stream_cli.alerts import AlertEngine, TriggeredAlert
from alpaca_stream_cli.alert_dispatcher import AlertDispatcher, DispatchResult
from alpaca_stream_cli.alert_throttle import AlertThrottleConfig
from alpaca_stream_cli.config import AlertConfig


def _make_engine(alerts: list[AlertConfig]) -> AlertEngine:
    return AlertEngine(alerts=alerts)


@pytest.fixture
def price_above_engine() -> AlertEngine:
    return _make_engine([
        AlertConfig(symbol="AAPL", condition="price_above", threshold=150.0),
    ])


@pytest.fixture
def open_throttle_cfg() -> AlertThrottleConfig:
    """Zero-interval throttle — never suppresses."""
    return AlertThrottleConfig(default_interval=0.0)


@pytest.fixture
def tight_throttle_cfg() -> AlertThrottleConfig:
    """Very long interval — suppresses after first fire."""
    return AlertThrottleConfig(default_interval=9999.0)


def test_dispatch_triggers_when_price_above(
    price_above_engine: AlertEngine,
    open_throttle_cfg: AlertThrottleConfig,
) -> None:
    dispatcher = AlertDispatcher(price_above_engine, throttle_config=open_throttle_cfg)
    result = dispatcher.dispatch("AAPL", price=155.0)
    assert len(result.dispatched) == 1
    assert result.dispatched[0].symbol == "AAPL"


def test_dispatch_no_trigger_below_threshold(
    price_above_engine: AlertEngine,
    open_throttle_cfg: AlertThrottleConfig,
) -> None:
    dispatcher = AlertDispatcher(price_above_engine, throttle_config=open_throttle_cfg)
    result = dispatcher.dispatch("AAPL", price=140.0)
    assert result.dispatched == []
    assert result.suppressed == 0


def test_second_dispatch_suppressed_by_throttle(
    price_above_engine: AlertEngine,
    tight_throttle_cfg: AlertThrottleConfig,
) -> None:
    dispatcher = AlertDispatcher(price_above_engine, throttle_config=tight_throttle_cfg)
    dispatcher.dispatch("AAPL", price=155.0)
    result = dispatcher.dispatch("AAPL", price=155.0)
    assert result.dispatched == []
    assert result.suppressed == 1


def test_notify_callback_called_on_dispatch(
    price_above_engine: AlertEngine,
    open_throttle_cfg: AlertThrottleConfig,
) -> None:
    callback = MagicMock()
    dispatcher = AlertDispatcher(
        price_above_engine,
        throttle_config=open_throttle_cfg,
        notify=callback,
    )
    dispatcher.dispatch("AAPL", price=160.0)
    callback.assert_called_once()
    arg = callback.call_args[0][0]
    assert isinstance(arg, TriggeredAlert)


def test_notify_not_called_when_suppressed(
    price_above_engine: AlertEngine,
    tight_throttle_cfg: AlertThrottleConfig,
) -> None:
    callback = MagicMock()
    dispatcher = AlertDispatcher(
        price_above_engine,
        throttle_config=tight_throttle_cfg,
        notify=callback,
    )
    dispatcher.dispatch("AAPL", price=155.0)
    dispatcher.dispatch("AAPL", price=155.0)
    assert callback.call_count == 1


def test_reset_symbol_allows_refiring(
    price_above_engine: AlertEngine,
    tight_throttle_cfg: AlertThrottleConfig,
) -> None:
    dispatcher = AlertDispatcher(price_above_engine, throttle_config=tight_throttle_cfg)
    dispatcher.dispatch("AAPL", price=155.0)
    dispatcher.reset_symbol("AAPL")
    result = dispatcher.dispatch("AAPL", price=155.0)
    assert len(result.dispatched) == 1


def test_set_notify_replaces_callback(
    price_above_engine: AlertEngine,
    open_throttle_cfg: AlertThrottleConfig,
) -> None:
    old_cb = MagicMock()
    new_cb = MagicMock()
    dispatcher = AlertDispatcher(
        price_above_engine,
        throttle_config=open_throttle_cfg,
        notify=old_cb,
    )
    dispatcher.set_notify(new_cb)
    dispatcher.dispatch("AAPL", price=155.0)
    old_cb.assert_not_called()
    new_cb.assert_called_once()
