"""Tests for alpaca_stream_cli.throttle."""

from __future__ import annotations

import time

import pytest

from alpaca_stream_cli.throttle import Throttle


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def throttle() -> Throttle:
    return Throttle(interval=0.5)


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

def test_invalid_interval_raises():
    with pytest.raises(ValueError):
        Throttle(interval=0)


def test_invalid_negative_interval_raises():
    with pytest.raises(ValueError):
        Throttle(interval=-1.0)


# ---------------------------------------------------------------------------
# allow()
# ---------------------------------------------------------------------------

def test_first_call_allowed(throttle: Throttle):
    assert throttle.allow("AAPL") is True


def test_second_immediate_call_blocked(throttle: Throttle):
    throttle.allow("AAPL")
    assert throttle.allow("AAPL") is False


def test_different_keys_are_independent(throttle: Throttle):
    throttle.allow("AAPL")
    assert throttle.allow("MSFT") is True


def test_allow_after_interval_passes(throttle: Throttle):
    throttle.allow("AAPL")
    time.sleep(0.55)
    assert throttle.allow("AAPL") is True


# ---------------------------------------------------------------------------
# fire_count()
# ---------------------------------------------------------------------------

def test_fire_count_increments(throttle: Throttle):
    throttle.allow("AAPL")
    time.sleep(0.55)
    throttle.allow("AAPL")
    assert throttle.fire_count("AAPL") == 2


def test_fire_count_unknown_key_is_zero(throttle: Throttle):
    assert throttle.fire_count("UNKNOWN") == 0


# ---------------------------------------------------------------------------
# reset()
# ---------------------------------------------------------------------------

def test_reset_allows_immediate_refire(throttle: Throttle):
    throttle.allow("AAPL")
    throttle.reset("AAPL")
    assert throttle.allow("AAPL") is True


def test_reset_unknown_key_does_not_raise(throttle: Throttle):
    throttle.reset("NONEXISTENT")  # should not raise


# ---------------------------------------------------------------------------
# reset_all()
# ---------------------------------------------------------------------------

def test_reset_all_clears_all_keys(throttle: Throttle):
    throttle.allow("AAPL")
    throttle.allow("MSFT")
    throttle.reset_all()
    assert throttle.allow("AAPL") is True
    assert throttle.allow("MSFT") is True


# ---------------------------------------------------------------------------
# time_until_next()
# ---------------------------------------------------------------------------

def test_time_until_next_none_for_unknown(throttle: Throttle):
    assert throttle.time_until_next("AAPL") is None


def test_time_until_next_positive_after_fire(throttle: Throttle):
    throttle.allow("AAPL")
    remaining = throttle.time_until_next("AAPL")
    assert remaining is not None
    assert 0 < remaining <= 0.5


def test_time_until_next_none_after_interval(throttle: Throttle):
    throttle.allow("AAPL")
    time.sleep(0.55)
    assert throttle.time_until_next("AAPL") is None
