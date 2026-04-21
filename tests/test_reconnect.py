"""Tests for alpaca_stream_cli.reconnect."""

from __future__ import annotations

import pytest

from alpaca_stream_cli.reconnect import ReconnectManager, ReconnectPolicy


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _no_sleep(seconds: float) -> None:  # noqa: ARG001
    """Drop-in replacement for time.sleep that does nothing."""


def _make_manager(**kwargs) -> ReconnectManager:
    policy = ReconnectPolicy(**kwargs)
    return ReconnectManager(policy=policy, sleep_fn=_no_sleep)


# ---------------------------------------------------------------------------
# Policy validation
# ---------------------------------------------------------------------------

def test_default_policy_values():
    policy = ReconnectPolicy()
    assert policy.base_delay == 1.0
    assert policy.max_delay == 60.0
    assert policy.multiplier == 2.0
    assert policy.max_attempts == 10


# ---------------------------------------------------------------------------
# Backoff calculation
# ---------------------------------------------------------------------------

def test_first_delay_equals_base():
    mgr = _make_manager(base_delay=2.0, multiplier=2.0)
    assert mgr.next_delay() == 2.0


def test_delay_grows_exponentially():
    mgr = _make_manager(base_delay=1.0, multiplier=3.0, max_delay=1000.0)
    delays = []
    for _ in range(4):
        delays.append(mgr.next_delay())
        mgr.state.record_attempt(delays[-1])
    assert delays == [1.0, 3.0, 9.0, 27.0]


def test_delay_capped_at_max():
    mgr = _make_manager(base_delay=1.0, multiplier=10.0, max_delay=5.0)
    for _ in range(5):
        delay = mgr.next_delay()
        mgr.state.record_attempt(delay)
    assert mgr.next_delay() == 5.0


# ---------------------------------------------------------------------------
# wait() behaviour
# ---------------------------------------------------------------------------

def test_wait_returns_true_when_attempts_remain():
    mgr = _make_manager(max_attempts=3)
    assert mgr.wait() is True


def test_wait_increments_attempt_count():
    mgr = _make_manager(max_attempts=5)
    mgr.wait()
    assert mgr.state.attempts == 1


def test_wait_returns_false_when_exhausted():
    mgr = _make_manager(max_attempts=2)
    mgr.wait()
    mgr.wait()
    assert mgr.exhausted
    assert mgr.wait() is False


# ---------------------------------------------------------------------------
# reset()
# ---------------------------------------------------------------------------

def test_reset_clears_attempts():
    mgr = _make_manager(max_attempts=5)
    mgr.wait()
    mgr.wait()
    mgr.reset()
    assert mgr.state.attempts == 0
    assert not mgr.exhausted


def test_reset_allows_fresh_backoff_sequence():
    mgr = _make_manager(base_delay=1.0, multiplier=2.0, max_attempts=5)
    for _ in range(3):
        mgr.wait()
    mgr.reset()
    assert mgr.next_delay() == 1.0


# ---------------------------------------------------------------------------
# exhausted property
# ---------------------------------------------------------------------------

def test_not_exhausted_initially():
    mgr = _make_manager(max_attempts=3)
    assert not mgr.exhausted


def test_exhausted_after_max_attempts():
    mgr = _make_manager(max_attempts=2)
    mgr.wait()
    mgr.wait()
    assert mgr.exhausted
