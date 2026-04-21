"""Tests for alpaca_stream_cli.alert_log_display."""

from datetime import datetime

import pytest
from rich.panel import Panel
from rich.table import Table

from alpaca_stream_cli.alert_log import AlertLog
from alpaca_stream_cli.alert_log_display import build_alert_log_table, render_alert_log_panel


@pytest.fixture()
def populated_log() -> AlertLog:
    log = AlertLog(max_entries=50)
    ts = datetime(2024, 6, 1, 10, 0, 0)
    log.record("AAPL", "price_above", 155.0, 150.0, triggered_at=ts)
    log.record("TSLA", "price_below", 198.0, 200.0, triggered_at=ts)
    log.record("MSFT", "volume_above", 1_200_000, 1_000_000, triggered_at=ts)
    return log


def test_build_alert_log_table_returns_table(populated_log: AlertLog) -> None:
    table = build_alert_log_table(populated_log)
    assert isinstance(table, Table)


def test_table_has_five_columns(populated_log: AlertLog) -> None:
    table = build_alert_log_table(populated_log)
    assert len(table.columns) == 5


def test_table_row_count_matches_entries(populated_log: AlertLog) -> None:
    table = build_alert_log_table(populated_log)
    assert table.row_count == 3


def test_table_respects_max_rows() -> None:
    log = AlertLog(max_entries=50)
    for i in range(20):
        log.record("AAPL", "price_above", float(i), 0.0)
    table = build_alert_log_table(log, max_rows=5)
    assert table.row_count == 5


def test_empty_log_produces_empty_table() -> None:
    log = AlertLog()
    table = build_alert_log_table(log)
    assert table.row_count == 0


def test_render_alert_log_panel_returns_panel(populated_log: AlertLog) -> None:
    panel = render_alert_log_panel(populated_log)
    assert isinstance(panel, Panel)


def test_panel_title_contains_count(populated_log: AlertLog) -> None:
    panel = render_alert_log_panel(populated_log)
    assert "3" in str(panel.title)
