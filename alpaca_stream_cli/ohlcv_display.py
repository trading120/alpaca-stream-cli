"""Rich display helpers for OHLCV bar data."""
from __future__ import annotations

from typing import List, Optional

from rich.table import Table
from rich import box

from alpaca_stream_cli.ohlcv_bar import OHLCVBar
from alpaca_stream_cli.formatter import format_price, format_volume, format_percent


def _change_color(pct: Optional[float]) -> str:
    if pct is None:
        return "dim"
    if pct > 0:
        return "green"
    if pct < 0:
        return "red"
    return "white"


def _fmt_change(bar: OHLCVBar) -> str:
    sign = "+" if bar.change >= 0 else ""
    color = _change_color(bar.change_pct)
    pct_str = format_percent(bar.change_pct)
    return f"[{color}]{sign}{format_price(bar.change)} ({pct_str})[/{color}]"


def build_ohlcv_table(bars: List[OHLCVBar], title: str = "OHLCV Bars") -> Table:
    """Build a Rich Table from a list of OHLCVBar objects."""
    table = Table(
        title=title,
        box=box.SIMPLE_HEAVY,
        show_header=True,
        header_style="bold cyan",
        expand=False,
    )
    table.add_column("Symbol", style="bold white", min_width=6)
    table.add_column("Open", justify="right")
    table.add_column("High", justify="right", style="green")
    table.add_column("Low", justify="right", style="red")
    table.add_column("Close", justify="right")
    table.add_column("Change", justify="right")
    table.add_column("Volume", justify="right")
    table.add_column("Range", justify="right", style="dim")

    for bar in bars:
        table.add_row(
            bar.symbol,
            format_price(bar.open),
            format_price(bar.high),
            format_price(bar.low),
            format_price(bar.close),
            _fmt_change(bar),
            format_volume(bar.volume),
            format_price(bar.range),
        )
    return table
