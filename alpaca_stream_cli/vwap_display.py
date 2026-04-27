"""Rich display helpers for VWAP data."""
from __future__ import annotations

from typing import Optional

from rich.table import Table
from rich import box

from alpaca_stream_cli.vwap_tracker import VWAPTracker
from alpaca_stream_cli.formatter import format_price, color_for_change


def _deviation_color(price: Optional[float], vwap: Optional[float]) -> str:
    """Return a color string based on price vs VWAP deviation."""
    if price is None or vwap is None or vwap == 0:
        return "white"
    diff_pct = (price - vwap) / vwap * 100
    if diff_pct > 0.5:
        return "green"
    if diff_pct < -0.5:
        return "red"
    return "yellow"


def _fmt_deviation(price: Optional[float], vwap: Optional[float]) -> str:
    """Format the percentage deviation of price from VWAP."""
    if price is None or vwap is None or vwap == 0:
        return "--"
    pct = (price - vwap) / vwap * 100
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.2f}%"


def build_vwap_table(
    symbols: list[str],
    tracker: VWAPTracker,
    prices: dict[str, Optional[float]],
) -> Table:
    """Build a Rich table showing VWAP and price deviation per symbol."""
    table = Table(
        title="VWAP",
        box=box.SIMPLE_HEAVY,
        show_header=True,
        header_style="bold cyan",
        expand=False,
    )
    table.add_column("Symbol", style="bold white", min_width=6)
    table.add_column("Last", justify="right", min_width=9)
    table.add_column("VWAP", justify="right", min_width=9)
    table.add_column("Deviation", justify="right", min_width=10)
    table.add_column("Trades", justify="right", min_width=7)

    for sym in symbols:
        key = sym.upper()
        vwap = tracker.get(key)
        price = prices.get(key)
        acc = tracker._symbols.get(key)
        trades = str(acc.trade_count) if acc else "0"

        color = _deviation_color(price, vwap)
        dev_str = _fmt_deviation(price, vwap)

        table.add_row(
            key,
            format_price(price),
            format_price(vwap),
            f"[{color}]{dev_str}[/{color}]",
            trades,
        )

    return table
