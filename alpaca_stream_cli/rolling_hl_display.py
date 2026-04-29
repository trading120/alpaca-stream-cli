"""Rich display table for rolling high/low tracker."""
from __future__ import annotations

from typing import Optional

from rich.table import Table
from rich import box

from alpaca_stream_cli.rolling_high_low import RollingHighLowTracker
from alpaca_stream_cli.formatter import format_price, format_percent


def _range_color(range_pct: Optional[float]) -> str:
    if range_pct is None:
        return "dim"
    if range_pct >= 3.0:
        return "bold red"
    if range_pct >= 1.5:
        return "yellow"
    if range_pct >= 0.5:
        return "green"
    return "dim"


def _fmt_price(value: Optional[float]) -> str:
    if value is None:
        return "[dim]---[/dim]"
    return format_price(value)


def _fmt_pct(value: Optional[float]) -> str:
    if value is None:
        return "[dim]---[/dim]"
    return format_percent(value)


def build_rolling_hl_table(
    tracker: RollingHighLowTracker,
    symbols: Optional[list[str]] = None,
    title: str = "Rolling High / Low",
) -> Table:
    syms = symbols if symbols is not None else tracker.symbols()

    table = Table(
        title=title,
        box=box.SIMPLE_HEAVY,
        show_header=True,
        header_style="bold white",
        expand=False,
    )
    table.add_column("Symbol", style="bold cyan", min_width=6)
    table.add_column("High", justify="right", min_width=10)
    table.add_column("Low", justify="right", min_width=10)
    table.add_column("Range", justify="right", min_width=10)
    table.add_column("Range %", justify="right", min_width=8)
    table.add_column("Samples", justify="right", min_width=7)

    for sym in syms:
        result = tracker.get(sym)
        if result is None:
            table.add_row(
                sym.upper(),
                "[dim]---[/dim]",
                "[dim]---[/dim]",
                "[dim]---[/dim]",
                "[dim]---[/dim]",
                "[dim]0[/dim]",
            )
            continue

        color = _range_color(result.range_pct)
        table.add_row(
            result.symbol,
            _fmt_price(result.high),
            _fmt_price(result.low),
            f"[{color}]{_fmt_price(result.range)}[/{color}]",
            f"[{color}]{_fmt_pct(result.range_pct)}[/{color}]",
            str(result.sample_count),
        )

    return table
