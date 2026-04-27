"""Rich display helpers for Bollinger Bands data."""
from __future__ import annotations

from typing import Dict, List, Optional

from rich.table import Table
from rich import box

from alpaca_stream_cli.bollinger_bands import BollingerResult


def _band_color(percent_b: Optional[float]) -> str:
    """Color based on price position within the bands."""
    if percent_b is None:
        return "dim"
    if percent_b >= 1.0:
        return "bold red"
    if percent_b >= 0.8:
        return "yellow"
    if percent_b <= 0.0:
        return "bold cyan"
    if percent_b <= 0.2:
        return "cyan"
    return "white"


def _fmt_price(value: Optional[float]) -> str:
    if value is None:
        return "---"
    return f"{value:,.4f}"


def _fmt_pct(value: Optional[float]) -> str:
    if value is None:
        return "---"
    return f"{value * 100:.2f}%"


def build_bollinger_table(
    symbols: List[str],
    results: Dict[str, Optional[BollingerResult]],
    *,
    title: str = "Bollinger Bands",
    max_rows: int = 50,
) -> Table:
    table = Table(
        title=title,
        box=box.SIMPLE_HEAVY,
        show_header=True,
        header_style="bold magenta",
        expand=False,
    )
    table.add_column("Symbol", style="bold white", min_width=6)
    table.add_column("Price", justify="right", min_width=10)
    table.add_column("Upper", justify="right", min_width=10)
    table.add_column("Middle (SMA)", justify="right", min_width=12)
    table.add_column("Lower", justify="right", min_width=10)
    table.add_column("%B", justify="right", min_width=7)
    table.add_column("Bandwidth", justify="right", min_width=10)

    for symbol in symbols[:max_rows]:
        r = results.get(symbol.upper())
        if r is None:
            table.add_row(
                symbol.upper(), "---", "---", "---", "---", "---", "---",
                style="dim",
            )
        else:
            color = _band_color(r.percent_b)
            table.add_row(
                r.symbol,
                _fmt_price(r.price),
                _fmt_price(r.upper),
                _fmt_price(r.middle),
                _fmt_price(r.lower),
                _fmt_pct(r.percent_b),
                _fmt_pct(r.bandwidth),
                style=color,
            )
    return table
