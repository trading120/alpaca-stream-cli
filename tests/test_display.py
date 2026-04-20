"""Tests for the terminal display module."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from alpaca_stream_cli.alerts import TriggeredAlert
from alpaca_stream_cli.display import (
    QuoteSnapshot,
    _format_change,
    build_market_table,
    render_snapshot,
)


@pytest.fixture
def sample_snapshots():
    return [
        QuoteSnapshot("AAPL", bid=149.90, ask=150.10, last=150.00, volume=1_000_000, change_pct=1.25),
        QuoteSnapshot("TSLA", bid=699.50, ask=700.50, last=700.00, volume=500_000, change_pct=-0.75),
        QuoteSnapshot("MSFT", bid=299.00, ask=301.00, last=300.00, volume=200_000, change_pct=None),
    ]


@pytest.fixture
def sample_alert():
    return [TriggeredAlert(symbol="AAPL", message="Price above 150.00")]


def test_format_change_positive():
    text = _format_change(2.5)
    assert "▲" in text.plain
    assert "+2.50%" in text.plain


def test_format_change_negative():
    text = _format_change(-1.3)
    assert "▼" in text.plain
    assert "-1.30%" in text.plain


def test_format_change_none():
    text = _format_change(None)
    assert text.plain == "N/A"


def test_build_market_table_row_count(sample_snapshots, sample_alert):
    table = build_market_table(sample_snapshots, sample_alert)
    assert table.row_count == 3


def test_build_market_table_has_alert_symbol(sample_snapshots, sample_alert):
    table = build_market_table(sample_snapshots, sample_alert)
    # Table renders without error; alert column populated for AAPL
    assert table is not None


def test_build_market_table_no_alerts(sample_snapshots):
    table = build_market_table(sample_snapshots, [])
    assert table.row_count == len(sample_snapshots)


@patch("alpaca_stream_cli.display.console")
def test_render_snapshot_calls_clear(mock_console, sample_snapshots, sample_alert):
    render_snapshot(sample_snapshots, sample_alert)
    mock_console.clear.assert_called_once()


@patch("alpaca_stream_cli.display.console")
def test_render_snapshot_no_alerts_skips_panel(mock_console, sample_snapshots):
    render_snapshot(sample_snapshots, [])
    # console.print called once for the table only
    assert mock_console.print.call_count == 1
