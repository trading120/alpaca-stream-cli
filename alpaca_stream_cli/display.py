"""Terminal display renderer for real-time market data."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.text import Text
except ImportError:
    raise ImportError("rich is required: pip install rich")

from alpaca_stream_cli.alerts import TriggeredAlert

console = Console()


@dataclass
class QuoteSnapshot:
    symbol: str
    bid: float
    ask: float
    last: float
    volume: int
    change_pct: Optional[float] = None
    timestamp: Optional[datetime] = None


def _format_change(change_pct: Optional[float]) -> Text:
    if change_pct is None:
        return Text("N/A", style="dim")
    arrow = "▲" if change_pct >= 0 else "▼"
    style = "green" if change_pct >= 0 else "red"
    return Text(f"{arrow} {change_pct:+.2f}%", style=style)


def build_market_table(snapshots: List[QuoteSnapshot], triggered: List[TriggeredAlert]) -> Table:
    """Build a Rich table from current quote snapshots."""
    alert_symbols = {a.symbol for a in triggered}

    table = Table(
        title=f"Market Data — {datetime.now().strftime('%H:%M:%S')}",
        show_lines=False,
        header_style="bold cyan",
    )
    table.add_column("Symbol", style="bold", width=8)
    table.add_column("Last", justify="right", width=10)
    table.add_column("Bid", justify="right", width=10)
    table.add_column("Ask", justify="right", width=10)
    table.add_column("Volume", justify="right", width=12)
    table.add_column("Change", justify="right", width=12)
    table.add_column("Alert", width=6)

    for snap in snapshots:
        alert_cell = Text("🔔", style="yellow bold") if snap.symbol in alert_symbols else Text("")
        table.add_row(
            snap.symbol,
            f"${snap.last:.2f}",
            f"${snap.bid:.2f}",
            f"${snap.ask:.2f}",
            f"{snap.volume:,}",
            _format_change(snap.change_pct),
            alert_cell,
        )

    return table


def render_alerts_panel(triggered: List[TriggeredAlert]) -> None:
    """Print triggered alerts below the market table."""
    if not triggered:
        return
    console.print("[bold yellow]⚠ Triggered Alerts:[/bold yellow]")
    for alert in triggered:
        console.print(f"  [yellow]{alert.symbol}[/yellow]: {alert.message}")


def render_snapshot(snapshots: List[QuoteSnapshot], triggered: List[TriggeredAlert]) -> None:
    """Clear terminal and render the full display."""
    console.clear()
    table = build_market_table(snapshots, triggered)
    console.print(table)
    render_alerts_panel(triggered)
