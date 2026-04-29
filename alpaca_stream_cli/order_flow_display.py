"""Rich display helpers for order flow imbalance data."""
from __future__ import annotations

from typing import List

from rich.table import Table
from rich import box

from alpaca_stream_cli.order_flow_imbalance import OrderFlowImbalanceTracker


def _ofi_color(ofi: float) -> str:
    if ofi > 0.4:
        return "bold green"
    if ofi > 0.1:
        return "green"
    if ofi < -0.4:
        return "bold red"
    if ofi < -0.1:
        return "red"
    return "white"


def _bar(ofi: float, width: int = 10) -> str:
    """ASCII bar centred at 0; positive = right, negative = left."""
    half = width // 2
    filled = int(abs(ofi) * half)
    filled = min(filled, half)
    if ofi >= 0:
        return " " * half + "█" * filled + " " * (half - filled)
    else:
        return " " * (half - filled) + "█" * filled + " " * half


def _fmt_ofi(ofi: float) -> str:
    return f"{ofi:+.3f}"


def _fmt_volume(vol: float) -> str:
    if vol >= 1_000_000:
        return f"{vol / 1_000_000:.2f}M"
    if vol >= 1_000:
        return f"{vol / 1_000:.1f}K"
    return f"{vol:.0f}"


def build_order_flow_table(
    tracker: OrderFlowImbalanceTracker,
    symbols: List[str],
) -> Table:
    table = Table(
        title="Order Flow Imbalance",
        box=box.SIMPLE_HEAVY,
        show_header=True,
        header_style="bold cyan",
        expand=False,
    )
    table.add_column("Symbol", style="bold white", min_width=6)
    table.add_column("OFI", justify="right", min_width=8)
    table.add_column("Label", min_width=11)
    table.add_column("Buy Vol", justify="right", min_width=8)
    table.add_column("Sell Vol", justify="right", min_width=8)
    table.add_column("Flow", min_width=12)

    for sym in symbols:
        result = tracker.get(sym)
        if result is None:
            table.add_row(sym.upper(), "—", "—", "—", "—", "—")
            continue
        color = _ofi_color(result.ofi)
        table.add_row(
            result.symbol,
            f"[{color}]{_fmt_ofi(result.ofi)}[/{color}]",
            f"[{color}]{result.label}[/{color}]",
            f"[green]{_fmt_volume(result.buy_volume)}[/green]",
            f"[red]{_fmt_volume(result.sell_volume)}[/red]",
            f"[{color}]{_bar(result.ofi)}[/{color}]",
        )
    return table
