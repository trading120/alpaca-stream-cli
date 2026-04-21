"""Tests for alpaca_stream_cli.connection_monitor."""

from __future__ import annotations

import pytest

from alpaca_stream_cli.connection_monitor import ConnectionMonitor, ConnectionStatus


@pytest.fixture()
def monitor() -> ConnectionMonitor:
    return ConnectionMonitor(max_events=10)


# ---------------------------------------------------------------------------
# Initial state
# ---------------------------------------------------------------------------

def test_initial_status_is_disconnected(monitor):
    assert monitor.status == ConnectionStatus.DISCONNECTED


def test_initial_is_not_connected(monitor):
    assert not monitor.is_connected


def test_initial_uptime_is_none(monitor):
    assert monitor.uptime is None


def test_initial_reconnect_count_is_zero(monitor):
    assert monitor.reconnect_count == 0


# ---------------------------------------------------------------------------
# Status transitions
# ---------------------------------------------------------------------------

def test_on_connecting_sets_status(monitor):
    monitor.on_connecting()
    assert monitor.status == ConnectionStatus.CONNECTING


def test_on_connected_sets_status(monitor):
    monitor.on_connected()
    assert monitor.status == ConnectionStatus.CONNECTED
    assert monitor.is_connected


def test_on_disconnected_sets_status(monitor):
    monitor.on_connected()
    monitor.on_disconnected()
    assert monitor.status == ConnectionStatus.DISCONNECTED
    assert not monitor.is_connected


def test_on_reconnecting_increments_count(monitor):
    monitor.on_reconnecting()
    monitor.on_reconnecting()
    assert monitor.reconnect_count == 2
    assert monitor.status == ConnectionStatus.RECONNECTING


def test_on_failed_sets_status(monitor):
    monitor.on_failed("auth error")
    assert monitor.status == ConnectionStatus.FAILED


# ---------------------------------------------------------------------------
# Uptime
# ---------------------------------------------------------------------------

def test_uptime_available_when_connected(monitor):
    monitor.on_connected()
    assert monitor.uptime is not None
    assert monitor.uptime >= 0.0


def test_uptime_none_after_disconnect(monitor):
    monitor.on_connected()
    monitor.on_disconnected()
    assert monitor.uptime is None


# ---------------------------------------------------------------------------
# Event log
# ---------------------------------------------------------------------------

def test_events_recorded_in_order(monitor):
    monitor.on_connecting("start")
    monitor.on_connected("ok")
    events = monitor.events()
    assert events[0].status == ConnectionStatus.CONNECTING
    assert events[1].status == ConnectionStatus.CONNECTED


def test_event_messages_stored(monitor):
    monitor.on_connecting("attempt 1")
    assert monitor.events()[0].message == "attempt 1"


def test_max_events_respected():
    mon = ConnectionMonitor(max_events=3)
    for _ in range(5):
        mon.on_connecting()
    assert len(mon.events()) == 3


def test_invalid_max_events_raises():
    with pytest.raises(ValueError):
        ConnectionMonitor(max_events=0)


# ---------------------------------------------------------------------------
# reset()
# ---------------------------------------------------------------------------

def test_reset_clears_state(monitor):
    monitor.on_connected()
    monitor.on_reconnecting()
    monitor.reset()
    assert monitor.status == ConnectionStatus.DISCONNECTED
    assert monitor.reconnect_count == 0
    assert monitor.events() == []
    assert monitor.uptime is None
