"""Tests for PriceAlertSummary."""
import pytest
from datetime import datetime, timezone

from alpaca_stream_cli.alert_log import AlertLog, AlertLogEntry
from alpaca_stream_cli.price_alert_summary import PriceAlertSummary, SymbolAlertSummary


def _entry(symbol: str, condition: str, price: float) -> AlertLogEntry:
    return AlertLogEntry(
        symbol=symbol,
        condition=condition,
        price=price,
        timestamp=datetime.now(timezone.utc),
    )


@pytest.fixture()
def log() -> AlertLog:
    return AlertLog(max_entries=50)


@pytest.fixture()
def summary(log: AlertLog) -> PriceAlertSummary:
    return PriceAlertSummary(log)


def test_build_empty_log_returns_empty_dict(summary):
    assert summary.build() == {}


def test_build_single_entry(log, summary):
    log.append(_entry("AAPL", "price_above", 150.0))
    result = summary.build()
    assert "AAPL" in result
    assert result["AAPL"].total_triggers == 1
    assert result["AAPL"].last_price == 150.0
    assert result["AAPL"].last_condition == "price_above"


def test_build_normalizes_symbol_to_uppercase(log, summary):
    log.append(_entry("aapl", "price_above", 150.0))
    result = summary.build()
    assert "AAPL" in result


def test_multiple_entries_same_symbol_accumulate(log, summary):
    log.append(_entry("TSLA", "price_above", 200.0))
    log.append(_entry("TSLA", "price_above", 210.0))
    log.append(_entry("TSLA", "price_below", 195.0))
    result = summary.build()
    assert result["TSLA"].total_triggers == 3
    assert result["TSLA"].last_price == 195.0
    assert set(result["TSLA"].conditions_seen) == {"price_above", "price_below"}


def test_multiple_symbols_are_independent(log, summary):
    log.append(_entry("AAPL", "price_above", 150.0))
    log.append(_entry("MSFT", "price_above", 300.0))
    result = summary.build()
    assert len(result) == 2
    assert result["AAPL"].total_triggers == 1
    assert result["MSFT"].total_triggers == 1


def test_for_symbol_returns_correct_summary(log, summary):
    log.append(_entry("NVDA", "price_above", 400.0))
    s = summary.for_symbol("NVDA")
    assert s is not None
    assert s.symbol == "NVDA"
    assert s.total_triggers == 1


def test_for_symbol_case_insensitive(log, summary):
    log.append(_entry("NVDA", "price_above", 400.0))
    assert summary.for_symbol("nvda") is not None


def test_for_symbol_missing_returns_none(summary):
    assert summary.for_symbol("XYZ") is None


def test_top_n_returns_sorted_by_trigger_count(log, summary):
    for _ in range(3):
        log.append(_entry("AAPL", "price_above", 150.0))
    for _ in range(5):
        log.append(_entry("TSLA", "price_above", 200.0))
    log.append(_entry("MSFT", "price_above", 300.0))
    top = summary.top_n(2)
    assert len(top) == 2
    assert top[0].symbol == "TSLA"
    assert top[1].symbol == "AAPL"


def test_top_n_invalid_raises():
    log = AlertLog()
    s = PriceAlertSummary(log)
    with pytest.raises(ValueError):
        s.top_n(0)


def test_invalid_log_type_raises():
    with pytest.raises(TypeError):
        PriceAlertSummary("not a log")  # type: ignore
