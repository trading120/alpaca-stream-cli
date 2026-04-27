"""Rich display helpers for momentum (rate-of-change) data."""
from __future__ import annotations

from typing import List, Optional

from rich.table import Table
from rich import box

from alpaca_stream_cli.momentum_tracker import MomentumTracker


def _roc_color(roc: Optional[float]) -> str:
    if roc is None:
        return "dim"
    if roc >= 2.0:
        return "bold green"
    if roc >= 0.5:
        return "green"
    if roc > -0.5:
        return "white"
    if roc > -2.0:
        return "red"
    return "bold red"


def _arrow(roc: Optional[float]) -> str:
    if roc is None:
        return "-"
    if roc >= 0.5:
        return "▲"
    if roc <= -0.5:
        return "▼"
    return "●"


def _fmt_roc(roc: Optional[float]) -> str:
    if roc is None:
        return "--"
    sign = "+" if roc >= 0 else ""
    return f"{sign}{roc:.2f}%"


def build_momentum_table(
    tracker: MomentumTracker,
    symbols: List[str],
    title: str = "Momentum (ROC)",
) -> Table:
    table = Table(
        title=title,
        box=box.SIMPLE_HEAVY,
        show_header=True,
        header_style="bold cyan",
        expand=False,
    )
    table.add_column("Symbol", style="bold white", min_width=8)
    table.add_column("Price", justify="right", min_width=10)
    table.add_column("ROC", justify="right", min_width=9)
    table.add_column("Dir", justify="center", min_width=4)
    table.add_column("Ticks", justify="right", min_width=6)

    for sym in symbols:
        entry = tracker.get(sym)
        if entry is None:
            table.add_row(sym.upper(), "--", "--", "-", "0")
            continue
        roc = entry.roc()
        color = _roc_color(roc)
        price = entry.latest_price()
        price_str = f"{price:.4f}" if price is not None else "--"
        table.add_row(
            sym.upper(),
            price_str,
            f"[{color}]{_fmt_roc(roc)}[/{color}]",
            f"[{color}]{_arrow(roc)}[/{color}]",
            str(entry.tick_count()),
        )

    return table
