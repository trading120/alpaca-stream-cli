"""Rich display helpers for quote spread data."""

from __future__ import annotations

from typing import Optional

from rich.table import Table
from rich import box

from alpaca_stream_cli.quote_spread_tracker import QuoteSpreadTracker


def _spread_color(spread_pct: Optional[float]) -> str:
    if spread_pct is None:
        return "dim"
    if spread_pct < 0.05:
        return "green"
    if spread_pct < 0.20:
        return "yellow"
    return "red"


def _fmt_spread(value: Optional[float], decimals: int = 4) -> str:
    if value is None:
        return "[dim]---[/dim]"
    return f"{value:.{decimals}f}"


def _fmt_pct(value: Optional[float]) -> str:
    if value is None:
        return "[dim]---[/dim]"
    color = _spread_color(value)
    return f"[{color}]{value:.4f}%[/{color}]"


def build_spread_table(tracker: QuoteSpreadTracker, title: str = "Quote Spreads") -> Table:
    """Build a Rich Table showing current spread info for all tracked symbols."""
    table = Table(
        title=title,
        box=box.SIMPLE_HEAVY,
        show_header=True,
        header_style="bold cyan",
        expand=False,
    )
    table.add_column("Symbol", style="bold white", no_wrap=True)
    table.add_column("Bid", justify="right")
    table.add_column("Ask", justify="right")
    table.add_column("Spread", justify="right")
    table.add_column("Spread %", justify="right")
    table.add_column("Avg Spread %", justify="right")

    for symbol in tracker.symbols():
        sym_tracker = tracker.get(symbol)
        if sym_tracker is None:
            continue
        latest = sym_tracker.latest()
        if latest is None:
            table.add_row(symbol, "---", "---", "---", "---", "---")
            continue

        avg_pct = sym_tracker.average_spread_pct()
        table.add_row(
            symbol,
            _fmt_spread(latest.bid),
            _fmt_spread(latest.ask),
            _fmt_spread(latest.spread),
            _fmt_pct(latest.spread_pct),
            _fmt_pct(avg_pct),
        )

    return table
