"""Rich display helpers for volume profile data."""
from __future__ import annotations

from typing import List, Optional

from rich.table import Table
from rich import box

from alpaca_stream_cli.volume_profile import VolumeProfileResult, VolumeProfileTracker


def _poc_color(poc: Optional[float], current: Optional[float]) -> str:
    if poc is None or current is None:
        return "dim"
    diff_pct = abs(current - poc) / poc * 100 if poc else 0
    if diff_pct < 0.5:
        return "bold magenta"
    if diff_pct < 1.5:
        return "magenta"
    return "white"


def _fmt_price(value: Optional[float]) -> str:
    if value is None:
        return "[dim]---[/dim]"
    return f"${value:,.2f}"


def _fmt_volume(value: float) -> str:
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:.0f}"


def build_volume_profile_table(
    tracker: VolumeProfileTracker,
    symbols: List[str],
    current_prices: Optional[dict] = None,
) -> Table:
    """Build a Rich Table summarising volume profile key levels."""
    table = Table(
        title="Volume Profile",
        box=box.SIMPLE_HEAD,
        show_lines=False,
        expand=False,
    )
    table.add_column("Symbol", style="bold cyan", min_width=6)
    table.add_column("POC", justify="right", min_width=9)
    table.add_column("VA Low", justify="right", min_width=9)
    table.add_column("VA High", justify="right", min_width=9)
    table.add_column("Total Vol", justify="right", min_width=10)

    prices = current_prices or {}

    for sym in symbols:
        result: Optional[VolumeProfileResult] = tracker.get(sym)
        if result is None:
            table.add_row(
                sym.upper(),
                "[dim]---[/dim]",
                "[dim]---[/dim]",
                "[dim]---[/dim]",
                "[dim]---[/dim]",
            )
            continue

        va_low, va_high = result.value_area()
        current = prices.get(sym.upper())
        color = _poc_color(result.poc, current)

        poc_str = f"[{color}]{_fmt_price(result.poc)}[/{color}]"
        table.add_row(
            sym.upper(),
            poc_str,
            _fmt_price(va_low) if va_low else "[dim]---[/dim]",
            _fmt_price(va_high) if va_high else "[dim]---[/dim]",
            _fmt_volume(result.total_volume),
        )

    return table
