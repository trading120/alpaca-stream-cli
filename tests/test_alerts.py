"""Tests for the AlertEngine class."""

import pytest
from alpaca_stream_cli.alerts import AlertEngine, TriggeredAlert
from alpaca_stream_cli.config import AlertConfig


@pytest.fixture
def basic_alerts():
    return [
        AlertConfig(symbol="AAPL", price_above=200.0, price_below=150.0),
        AlertConfig(symbol="TSLA", volume_above=1_000_000),
    ]


def test_price_above_triggers(basic_alerts):
    engine = AlertEngine(basic_alerts)
    fired = engine.evaluate("AAPL", price=210.0)
    assert len(fired) == 1
    assert "200.0" in fired[0].condition


def test_price_below_triggers(basic_alerts):
    engine = AlertEngine(basic_alerts)
    fired = engine.evaluate("AAPL", price=140.0)
    assert len(fired) == 1
    assert "150.0" in fired[0].condition


def test_no_trigger_within_range(basic_alerts):
    engine = AlertEngine(basic_alerts)
    fired = engine.evaluate("AAPL", price=175.0)
    assert fired == []


def test_volume_alert_triggers(basic_alerts):
    engine = AlertEngine(basic_alerts)
    fired = engine.evaluate("TSLA", price=700.0, volume=2_000_000)
    assert len(fired) == 1
    assert "volume" in fired[0].condition


def test_alert_fires_only_once(basic_alerts):
    engine = AlertEngine(basic_alerts)
    engine.evaluate("AAPL", price=210.0)
    fired_again = engine.evaluate("AAPL", price=215.0)
    assert fired_again == []


def test_reset_clears_triggered_state(basic_alerts):
    engine = AlertEngine(basic_alerts)
    engine.evaluate("AAPL", price=210.0)
    engine.reset("AAPL")
    fired = engine.evaluate("AAPL", price=220.0)
    assert len(fired) == 1


def test_reset_all_clears_all_symbols(basic_alerts):
    """Resetting all symbols allows alerts to fire again for every symbol."""
    engine = AlertEngine(basic_alerts)
    engine.evaluate("AAPL", price=210.0)
    engine.evaluate("TSLA", volume=2_000_000)
    engine.reset()
    fired_aapl = engine.evaluate("AAPL", price=220.0)
    fired_tsla = engine.evaluate("TSLA", volume=3_000_000)
    assert len(fired_aapl) == 1
    assert len(fired_tsla) == 1


def test_callback_is_called(basic_alerts):
    received = []
    engine = AlertEngine(basic_alerts, callback=received.append)
    engine.evaluate("AAPL", price=210.0)
    assert len(received) == 1
    assert isinstance(received[0], TriggeredAlert)


def test_unrelated_symbol_not_triggered(basic_alerts):
    engine = AlertEngine(basic_alerts)
    fired = engine.evaluate("GOOG", price=5000.0)
    assert fired == []
