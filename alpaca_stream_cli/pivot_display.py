"""Rich table rendering for pivot point data."""
from __future__ import annotations

from typing import List

from rich.table import Table
from rich import box

from alpaca_stream_cli.pivot_points import PivotPointTracker, PivotResult
from alpaca_stream_cli.formatter import format_price


def _level_color(price: float, level: float, tolerance: float = 0.005) -> str:
    """Highlight a level if current price is within *tolerance* fraction."""
    if price <= 0:
        return "white"
    diff_pct = abs(price - level) / price
    if diff_pct <= tolerance:
        return "bold yellow"
    if level > price:
        return "green"
    return "red"


def _fmt(value: float) -> str:
    return format_price(value)


def build_pivot_table(
    tracker: PivotPointTracker,
    symbols: List[str],
    current_prices: dict[str, float] | None = None,
) -> Table:
    """Return a Rich Table with pivot levels for each symbol."""
    prices = current_prices or {}
    table = Table(
        title="Pivot Points",
        box=box.SIMPLE_HEAVY,
        show_header=True,
        header_style="bold cyan",
        expand=False,
    )
    for col in ("Symbol", "Pivot", "R1", "R2", "R3", "S1", "S2", "S3"):
        table.add_column(col, justify="right" if col != "Symbol" else "left")

    for sym in symbols:
        result: PivotResult | None = tracker.get(sym)
        price = prices.get(sym.upper(), 0.0)
        if result is None:
            table.add_row(sym.upper(), *(["—"] * 7))
            continue

        def _c(level: float) -> str:
            return f"[{_level_color(price, level)}]{_fmt(level)}[/]"

        table.add_row(
            f"[bold]{result.symbol}[/]",
            f"[bold white]{_fmt(result.pivot)}[/]",
            _c(result.r1), _c(result.r2), _c(result.r3),
            _c(result.s1), _c(result.s2), _c(result.s3),
        )
    return table
