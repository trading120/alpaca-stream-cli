"""Rich display table for breakout tracker results."""
from __future__ import annotations

from typing import Sequence

from rich.table import Table
from rich import box
from rich.text import Text

from alpaca_stream_cli.breakout_tracker import BreakoutResult, BreakoutTracker


def _breakout_color(result: BreakoutResult) -> str:
    if result.breakout_up:
        return "bold green"
    if result.breakout_down:
        return "bold red"
    return "white"


def _fmt_price(price: float) -> str:
    return f"${price:,.2f}"


def _fmt_pct(pct: float | None) -> str:
    if pct is None:
        return "—"
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.2f}%"


def _direction_label(result: BreakoutResult) -> Text:
    if result.breakout_up:
        return Text("▲ UP", style="bold green")
    if result.breakout_down:
        return Text("▼ DOWN", style="bold red")
    return Text("— RANGE", style="dim")


def build_breakout_table(
    tracker: BreakoutTracker,
    symbols: Sequence[str],
) -> Table:
    table = Table(
        title="Breakout Tracker",
        box=box.SIMPLE_HEAVY,
        show_lines=False,
        expand=False,
    )
    table.add_column("Symbol", style="bold cyan", min_width=6)
    table.add_column("Price", justify="right", min_width=9)
    table.add_column("Upper", justify="right", min_width=9)
    table.add_column("Lower", justify="right", min_width=9)
    table.add_column("Direction", justify="center", min_width=8)
    table.add_column("Breakout %", justify="right", min_width=10)

    for sym in symbols:
        result = tracker.get(sym)
        if result is None:
            table.add_row(sym.upper(), "—", "—", "—", Text("—", style="dim"), "—")
            continue
        color = _breakout_color(result)
        pct = result.pct_above_upper if result.breakout_up else result.pct_below_lower
        table.add_row(
            Text(result.symbol, style=color),
            _fmt_price(result.price),
            _fmt_price(result.upper),
            _fmt_price(result.lower),
            _direction_label(result),
            _fmt_pct(pct),
        )
    return table
