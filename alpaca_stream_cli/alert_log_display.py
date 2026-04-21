"""Rich renderable panel for the alert log."""

from __future__ import annotations

from rich.panel import Panel
from rich.table import Table
from rich import box

from alpaca_stream_cli.alert_log import AlertLog

_CONDITION_COLORS = {
    "price_above": "green",
    "price_below": "red",
    "volume_above": "cyan",
}
_DEFAULT_COLOR = "yellow"


def _condition_color(condition: str) -> str:
    return _CONDITION_COLORS.get(condition, _DEFAULT_COLOR)


def build_alert_log_table(log: AlertLog, max_rows: int = 15) -> Table:
    """Build a Rich Table from the *max_rows* most recent log entries."""
    table = Table(
        box=box.SIMPLE_HEAVY,
        show_header=True,
        header_style="bold white",
        expand=True,
    )
    table.add_column("Time", style="dim", width=10, no_wrap=True)
    table.add_column("Symbol", width=8, no_wrap=True)
    table.add_column("Condition", width=14)
    table.add_column("Value", justify="right", width=12)
    table.add_column("Threshold", justify="right", width=12)

    for entry in log.recent(max_rows):
        color = _condition_color(entry.condition)
        ts = entry.triggered_at.strftime("%H:%M:%S")
        table.add_row(
            ts,
            f"[bold]{entry.symbol}[/bold]",
            f"[{color}]{entry.condition}[/{color}]",
            f"{entry.value:.4f}",
            f"{entry.threshold:.4f}",
        )

    return table


def render_alert_log_panel(log: AlertLog, max_rows: int = 15) -> Panel:
    """Wrap the alert log table in a Rich Panel."""
    table = build_alert_log_table(log, max_rows=max_rows)
    title = f"Alert Log ({len(log)} total)"
    return Panel(table, title=title, border_style="yellow")
