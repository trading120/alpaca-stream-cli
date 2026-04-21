"""Tests for alpaca_stream_cli.alert_log."""

from datetime import datetime

import pytest

from alpaca_stream_cli.alert_log import AlertLog, AlertLogEntry


@pytest.fixture()
def log() -> AlertLog:
    return AlertLog(max_entries=5)


def test_record_returns_entry(log: AlertLog) -> None:
    entry = log.record("aapl", "price_above", 155.0, 150.0)
    assert isinstance(entry, AlertLogEntry)
    assert entry.symbol == "AAPL"
    assert entry.condition == "price_above"
    assert entry.value == 155.0
    assert entry.threshold == 150.0


def test_record_normalizes_symbol_to_uppercase(log: AlertLog) -> None:
    entry = log.record("tsla", "price_below", 200.0, 210.0)
    assert entry.symbol == "TSLA"


def test_len_increases_with_records(log: AlertLog) -> None:
    assert len(log) == 0
    log.record("AAPL", "price_above", 1.0, 1.0)
    assert len(log) == 1
    log.record("AAPL", "price_above", 2.0, 1.0)
    assert len(log) == 2


def test_max_entries_respected(log: AlertLog) -> None:
    for i in range(10):
        log.record("AAPL", "price_above", float(i), 0.0)
    assert len(log) == 5  # bounded by max_entries


def test_recent_returns_last_n(log: AlertLog) -> None:
    for i in range(5):
        log.record("AAPL", "price_above", float(i), 0.0)
    recent = log.recent(3)
    assert len(recent) == 3
    assert recent[-1].value == 4.0


def test_recent_all_when_n_exceeds_length(log: AlertLog) -> None:
    log.record("AAPL", "price_above", 1.0, 0.0)
    assert len(log.recent(100)) == 1


def test_for_symbol_filters_correctly(log: AlertLog) -> None:
    log.record("AAPL", "price_above", 1.0, 0.0)
    log.record("TSLA", "price_below", 2.0, 3.0)
    log.record("aapl", "volume_above", 5.0, 4.0)
    aapl_entries = log.for_symbol("AAPL")
    assert len(aapl_entries) == 2
    assert all(e.symbol == "AAPL" for e in aapl_entries)


def test_clear_empties_log(log: AlertLog) -> None:
    log.record("AAPL", "price_above", 1.0, 0.0)
    log.clear()
    assert len(log) == 0


def test_invalid_max_entries_raises() -> None:
    with pytest.raises(ValueError):
        AlertLog(max_entries=0)


def test_str_representation() -> None:
    ts = datetime(2024, 1, 15, 9, 30, 0)
    entry = AlertLogEntry("AAPL", "price_above", 155.0, 150.0, triggered_at=ts)
    result = str(entry)
    assert "09:30:00" in result
    assert "AAPL" in result
    assert "price_above" in result
