"""Rich display helpers for ATR (Average True Range) data."""
from __future__ import annotations

from typing import Optional

from rich.table import Table
from rich import box

from alpaca_stream_cli.atr_tracker import ATRTracker


def _volatility_color(atr: Optional[float], price: Optional[float]) -> str:
    """Return a color based on ATR as a percentage of price."""
    if atr is None or price is None or price == 0:
        return "dim"
    pct = (atr / price) * 100
    if pct >= 5.0:
        return "bold red"
    if pct >= 2.0:
        return "yellow"
    if pct >= 0.5:
        return "green"
    return "dim"


def _fmt_atr(value: Optional[float]) -> str:
    if value is None:
        return "[dim]---[/dim]"
    return f"{value:.4f}"


def _fmt_pct(atr: Optional[float], price: Optional[float]) -> str:
    if atr is None or price is None or price == 0:
        return "[dim]---[/dim]"
    pct = (atr / price) * 100
    return f"{pct:.2f}%"


def build_atr_table(
    tracker: ATRTracker,
    prices: dict[str, float] | None = None,
    max_rows: int = 50,
) -> Table:
    """Build a Rich table showing ATR values for tracked symbols."""
    prices = prices or {}
    table = Table(
        title="Average True Range (ATR)",
        box=box.SIMPLE_HEAVY,
        show_lines=False,
        expand=False,
    )
    table.add_column("Symbol", style="bold white", min_width=8)
    table.add_column("ATR", justify="right", min_width=10)
    table.add_column("ATR %", justify="right", min_width=8)
    table.add_column("Trades", justify="right", min_width=7)
    table.add_column("Volatility", justify="center", min_width=10)

    symbols = tracker.symbols()[:max_rows]
    for sym in symbols:
        sa = tracker._symbols[sym]
        atr = sa.value
        price = prices.get(sym)
        color = _volatility_color(atr, price)
        if atr is None:
            vol_label = "[dim]warming up[/dim]"
        elif price and (atr / price) * 100 >= 5.0:
            vol_label = f"[{color}]HIGH[/{color}]"
        elif price and (atr / price) * 100 >= 2.0:
            vol_label = f"[{color}]MED[/{color}]"
        elif price and (atr / price) * 100 >= 0.5:
            vol_label = f"[{color}]LOW[/{color}]"
        else:
            vol_label = f"[{color}]FLAT[/{color}]"

        table.add_row(
            f"[bold]{sym}[/bold]",
            f"[{color}]{_fmt_atr(atr)}[/{color}]",
            _fmt_pct(atr, price),
            str(sa.trade_count),
            vol_label,
        )
    return table
