"""Rich table display for gap tracker results."""
from __future__ import annotations

from typing import Dict, List

from rich.table import Table
from rich import box

from alpaca_stream_cli.gap_tracker import GapResult
from alpaca_stream_cli.formatter import format_price, format_percent


def _gap_color(gap_pct: float) -> str:
    if gap_pct >= 3.0:
        return "bold green"
    if gap_pct >= 1.0:
        return "green"
    if gap_pct <= -3.0:
        return "bold red"
    if gap_pct <= -1.0:
        return "red"
    return "white"


def _fmt_gap(gap: float) -> str:
    sign = "+" if gap >= 0 else ""
    return f"{sign}{gap:.4f}"


def _fmt_filled(filled: bool) -> str:
    return "[green]YES[/green]" if filled else "[dim]no[/dim]"


def build_gap_table(
    results: Dict[str, GapResult],
    symbols: List[str],
    title: str = "Overnight Gaps",
) -> Table:
    table = Table(
        title=title,
        box=box.SIMPLE_HEAD,
        show_header=True,
        header_style="bold cyan",
        expand=False,
    )
    table.add_column("Symbol", style="bold white", width=8)
    table.add_column("Prev Close", justify="right", width=11)
    table.add_column("Open", justify="right", width=11)
    table.add_column("Gap", justify="right", width=10)
    table.add_column("Gap %", justify="right", width=9)
    table.add_column("Filled", justify="center", width=7)

    for sym in symbols:
        key = sym.upper()
        r = results.get(key)
        if r is None:
            table.add_row(key, "—", "—", "—", "—", "—")
            continue
        color = _gap_color(r.gap_pct)
        table.add_row(
            key,
            format_price(r.prev_close),
            format_price(r.open_price),
            f"[{color}]{_fmt_gap(r.gap)}[/{color}]",
            f"[{color}]{format_percent(r.gap_pct)}[/{color}]",
            _fmt_filled(r.filled),
        )
    return table
