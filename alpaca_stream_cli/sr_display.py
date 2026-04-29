"""Rich display table for support/resistance levels."""
from __future__ import annotations

from typing import Optional

from rich.table import Table
from rich import box
from rich.text import Text

from alpaca_stream_cli.support_resistance import SRResult, SupportResistanceTracker


def _level_color(price: Optional[float], level: Optional[float], is_support: bool) -> str:
    if price is None or level is None:
        return "dim"
    pct = abs(price - level) / price
    if pct < 0.005:
        return "bold yellow"
    return "green" if is_support else "red"


def _fmt_price(value: Optional[float]) -> str:
    if value is None:
        return "--"
    return f"${value:,.2f}"


def _fmt_distance(price: Optional[float], level: Optional[float]) -> str:
    if price is None or level is None:
        return "--"
    pct = (level - price) / price * 100
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.2f}%"


def build_sr_table(
    symbols: list[str],
    tracker: SupportResistanceTracker,
    max_rows: int = 20,
) -> Table:
    table = Table(
        box=box.SIMPLE_HEAD,
        show_header=True,
        header_style="bold cyan",
        expand=False,
    )
    table.add_column("Symbol", style="bold white", width=8)
    table.add_column("Last", justify="right", width=10)
    table.add_column("Support", justify="right", width=10)
    table.add_column("S-Dist", justify="right", width=8)
    table.add_column("Resistance", justify="right", width=10)
    table.add_column("R-Dist", justify="right", width=8)
    table.add_column("Zone", justify="center", width=10)

    for sym in symbols[:max_rows]:
        result = tracker.result(sym)
        if result is None:
            table.add_row(sym.upper(), "--", "--", "--", "--", "--", Text("--", style="dim"))
            continue

        s_color = _level_color(result.last_price, result.support, is_support=True)
        r_color = _level_color(result.last_price, result.resistance, is_support=False)

        if result.near_support:
            zone = Text("SUPPORT", style="bold green")
        elif result.near_resistance:
            zone = Text("RESIST", style="bold red")
        else:
            zone = Text("mid", style="dim")

        table.add_row(
            sym.upper(),
            _fmt_price(result.last_price),
            Text(_fmt_price(result.support), style=s_color),
            _fmt_distance(result.last_price, result.support),
            Text(_fmt_price(result.resistance), style=r_color),
            _fmt_distance(result.last_price, result.resistance),
            zone,
        )

    return table
