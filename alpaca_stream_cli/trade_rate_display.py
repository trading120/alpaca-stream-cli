"""Rich display helpers for per-symbol trade rate (TPS) data."""
from __future__ import annotations

from typing import Dict, Optional

from rich.table import Table
from rich import box
from rich.text import Text

from alpaca_stream_cli.trade_rate import TradeRateTracker


def _rate_color(tps: float) -> str:
    """Map a TPS value to a display colour."""
    if tps >= 5.0:
        return "bright_red"
    if tps >= 2.0:
        return "yellow"
    if tps > 0.0:
        return "green"
    return "dim white"


def _fmt_rate(tps: float) -> Text:
    color = _rate_color(tps)
    return Text(f"{tps:.2f}", style=color)


def _fmt_count(n: int) -> Text:
    color = "bright_white" if n > 0 else "dim white"
    return Text(str(n), style=color)


def build_trade_rate_table(
    tracker: TradeRateTracker,
    symbols: Optional[list[str]] = None,
    title: str = "Trade Rate",
) -> Table:
    """Build a Rich Table showing TPS and window count for each symbol."""
    table = Table(
        title=title,
        box=box.SIMPLE_HEAD,
        show_header=True,
        header_style="bold cyan",
        expand=False,
    )
    table.add_column("Symbol", style="bold white", min_width=6)
    table.add_column("TPS", justify="right", min_width=7)
    table.add_column("Count (window)", justify="right", min_width=14)

    targets = symbols if symbols is not None else tracker.symbols()

    for sym in sorted(s.upper() for s in targets):
        tps = tracker.rate(sym)
        cnt = tracker.count(sym)
        table.add_row(
            Text(sym, style="bold white"),
            _fmt_rate(tps),
            _fmt_count(cnt),
        )

    return table
