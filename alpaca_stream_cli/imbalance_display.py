"""Rich display components for bid/ask imbalance data."""
from __future__ import annotations

from typing import Optional

from rich.table import Table
from rich import box

from alpaca_stream_cli.bid_ask_imbalance import BidAskImbalanceTracker


def _imbalance_bar(value: float, width: int = 10) -> str:
    """Render a simple ASCII bar representing imbalance in [-1, 1]."""
    filled = int(abs(value) * width)
    filled = min(filled, width)
    if value >= 0:
        return "[green]" + "█" * filled + "░" * (width - filled) + "[/green]"
    else:
        return "[red]" + "█" * filled + "░" * (width - filled) + "[/red]"


def _imbalance_color(value: Optional[float]) -> str:
    if value is None:
        return "dim"
    if value > 0.2:
        return "green"
    if value < -0.2:
        return "red"
    return "yellow"


def _fmt_imbalance(value: Optional[float]) -> str:
    if value is None:
        return "--"
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.3f}"


def build_imbalance_table(
    tracker: BidAskImbalanceTracker,
    symbols: list[str],
    title: str = "Bid/Ask Imbalance",
) -> Table:
    table = Table(
        title=title,
        box=box.SIMPLE_HEAVY,
        show_header=True,
        header_style="bold cyan",
        expand=False,
    )
    table.add_column("Symbol", style="bold white", width=8)
    table.add_column("Latest", justify="right", width=8)
    table.add_column("Average", justify="right", width=8)
    table.add_column("Pressure", justify="left", width=14)

    for sym in symbols:
        latest = tracker.latest_imbalance(sym)
        average = tracker.average_imbalance(sym)
        color = _imbalance_color(latest)
        bar = _imbalance_bar(latest if latest is not None else 0.0)
        table.add_row(
            sym.upper(),
            f"[{color}]{_fmt_imbalance(latest)}[/{color}]",
            f"[{color}]{_fmt_imbalance(average)}[/{color}]",
            bar,
        )

    return table
