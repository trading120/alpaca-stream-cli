"""Display table for Bollinger Bands data using Rich."""

from __future__ import annotations

from typing import Sequence

from rich.style import Style
from rich.table import Table

from alpaca_stream_cli.bollinger_bands import BollingerResult, SymbolBollinger


# ── colour helpers ────────────────────────────────────────────────────────────

def _band_color(result: BollingerResult | None) -> Style:
    """Return a style based on where price sits relative to the bands."""
    if result is None:
        return Style(dim=True)
    pb = result.percent_b
    if pb is None:
        return Style(dim=True)
    if pb > 1.0:
        return Style(color="red", bold=True)   # above upper band
    if pb >= 0.8:
        return Style(color="red")              # approaching upper band
    if pb <= 0.0:
        return Style(color="green", bold=True) # below lower band
    if pb <= 0.2:
        return Style(color="green")            # approaching lower band
    return Style(color="white")                # within bands


def _fmt_price(value: float | None, *, prefix: str = "") -> str:
    """Format an optional price value."""
    if value is None:
        return "--"
    return f"{prefix}${value:,.2f}"


def _fmt_pct(value: float | None) -> str:
    """Format an optional percent-B value as a percentage string."""
    if value is None:
        return "--"
    return f"{value * 100:.1f}%"


# ── table builder ─────────────────────────────────────────────────────────────

def build_bollinger_table(
    symbols: Sequence[str],
    tracker: SymbolBollinger,
    *,
    title: str = "Bollinger Bands",
) -> Table:
    """Build a Rich Table showing Bollinger Band metrics for each symbol.

    Columns: Symbol | Upper | Middle (SMA) | Lower | Price | %B

    Args:
        symbols:  Ordered list of ticker symbols to display.
        tracker:  A :class:`SymbolBollinger` instance that holds per-symbol state.
        title:    Optional table title.

    Returns:
        A fully populated :class:`rich.table.Table`.
    """
    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("Symbol", style="bold", min_width=6)
    table.add_column("Upper",  justify="right", min_width=10)
    table.add_column("SMA",    justify="right", min_width=10)
    table.add_column("Lower",  justify="right", min_width=10)
    table.add_column("Price",  justify="right", min_width=10)
    table.add_column("%B",     justify="right", min_width=7)

    for sym in symbols:
        result: BollingerResult | None = tracker.result(sym)
        color = _band_color(result)

        if result is None:
            table.add_row(
                sym.upper(),
                "--", "--", "--", "--", "--",
                style=Style(dim=True),
            )
        else:
            table.add_row(
                sym.upper(),
                _fmt_price(result.upper),
                _fmt_price(result.middle),
                _fmt_price(result.lower),
                _fmt_price(result.price),
                _fmt_pct(result.percent_b),
                style=color,
            )

    return table
