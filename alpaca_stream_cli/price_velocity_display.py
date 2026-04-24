"""Display helpers for price velocity / momentum indicators."""

from __future__ import annotations

from typing import Optional

from rich.table import Table
from rich.text import Text
from rich import box

from alpaca_stream_cli.price_change_tracker import PriceChangeTracker
from alpaca_stream_cli.formatter import format_price, format_percent, color_for_change


def _arrow(pct: Optional[float]) -> Text:
    """Return a coloured directional arrow based on percent change."""
    if pct is None:
        return Text("  —", style="dim")
    if pct > 0.5:
        return Text(" ▲▲", style="bold green")
    if pct > 0:
        return Text("  ▲", style="green")
    if pct < -0.5:
        return Text(" ▼▼", style="bold red")
    if pct < 0:
        return Text("  ▼", style="red")
    return Text("  —", style="dim")


def _fmt_pct(pct: Optional[float]) -> Text:
    if pct is None:
        return Text("  —", style="dim")
    style = color_for_change(pct)
    return Text(format_percent(pct), style=style)


def build_velocity_table(
    symbols: list[str],
    tracker: PriceChangeTracker,
    window_seconds: float = 60.0,
    title: str = "Price Momentum",
) -> Table:
    """Build a Rich Table showing short-window price velocity for each symbol."""
    table = Table(
        title=title,
        box=box.SIMPLE_HEAVY,
        show_edge=False,
        header_style="bold cyan",
        expand=False,
    )
    table.add_column("Symbol", style="bold white", min_width=7)
    table.add_column("Last", justify="right", min_width=9)
    table.add_column(f"Δ {int(window_seconds)}s", justify="right", min_width=9)
    table.add_column("%", justify="right", min_width=8)
    table.add_column(" ", min_width=3)

    for sym in symbols:
        upper = sym.upper()
        latest = tracker.latest_price(upper)
        change = tracker.change_over_window(upper, window_seconds)
        pct = tracker.pct_change_over_window(upper, window_seconds)

        last_txt = Text(format_price(latest), style="white") if latest else Text("—", style="dim")
        change_txt = (
            Text(format_price(abs(change), currency=""), style=color_for_change(change))
            if change is not None
            else Text("—", style="dim")
        )

        table.add_row(upper, last_txt, change_txt, _fmt_pct(pct), _arrow(pct))

    return table
