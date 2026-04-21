"""Tests for AlertThrottle — per-(symbol, condition) alert rate limiting."""

from __future__ import annotations

import time

import pytest

from alpaca_stream_cli.alert_throttle import AlertThrottle, AlertThrottleConfig


@pytest.fixture
def throttle() -> AlertThrottle:
    cfg = AlertThrottleConfig(default_interval=1.0)
    return AlertThrottle(config=cfg)


def test_first_alert_is_allowed(throttle: AlertThrottle) -> None:
    assert throttle.allow("AAPL", "price_above") is True


def test_second_immediate_alert_is_blocked(throttle: AlertThrottle) -> None:
    throttle.allow("AAPL", "price_above")
    assert throttle.allow("AAPL", "price_above") is False


def test_different_conditions_are_independent(throttle: AlertThrottle) -> None:
    throttle.allow("AAPL", "price_above")
    assert throttle.allow("AAPL", "price_below") is True


def test_different_symbols_are_independent(throttle: AlertThrottle) -> None:
    throttle.allow("AAPL", "price_above")
    assert throttle.allow("TSLA", "price_above") is True


def test_symbol_normalized_to_uppercase(throttle: AlertThrottle) -> None:
    throttle.allow("aapl", "price_above")
    assert throttle.allow("AAPL", "price_above") is False


def test_reset_allows_refiring(throttle: AlertThrottle) -> None:
    throttle.allow("AAPL", "price_above")
    throttle.reset("AAPL", "price_above")
    assert throttle.allow("AAPL", "price_above") is True


def test_reset_symbol_clears_all_conditions(throttle: AlertThrottle) -> None:
    throttle.allow("AAPL", "price_above")
    throttle.allow("AAPL", "price_below")
    throttle.reset_symbol("AAPL")
    assert throttle.allow("AAPL", "price_above") is True
    assert throttle.allow("AAPL", "price_below") is True


def test_reset_symbol_does_not_affect_other_symbols(throttle: AlertThrottle) -> None:
    throttle.allow("AAPL", "price_above")
    throttle.allow("TSLA", "price_above")
    throttle.reset_symbol("AAPL")
    assert throttle.allow("TSLA", "price_above") is False


def test_per_symbol_override_interval() -> None:
    cfg = AlertThrottleConfig(
        default_interval=60.0,
        per_symbol_overrides={"TSLA": 0.0},
    )
    at = AlertThrottle(config=cfg)
    at.allow("TSLA", "price_above")
    time.sleep(0.01)
    assert at.allow("TSLA", "price_above") is True


def test_active_keys_tracks_seen_pairs(throttle: AlertThrottle) -> None:
    throttle.allow("AAPL", "price_above")
    throttle.allow("AAPL", "price_below")
    throttle.allow("TSLA", "volume")
    keys = throttle.active_keys()
    assert "AAPL:price_above" in keys
    assert "AAPL:price_below" in keys
    assert "TSLA:volume" in keys
    assert len(keys) == 3


def test_default_config_used_when_none_provided() -> None:
    at = AlertThrottle()
    assert at.allow("AAPL", "price_above") is True
    assert at.allow("AAPL", "price_above") is False
