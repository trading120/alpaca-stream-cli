"""Unified indicator display panel combining RSI, EMA, MACD, and Stochastic.

Provides a consolidated Rich table showing all technical indicators for
each symbol in the watchlist, making it easy to scan signal confluence.
"""

from __future__ import annotations

from typing import Iterable

from rich.table import Table
from rich import box

from alpaca_stream_cli.rsi_tracker import SymbolRSI
from alpaca_stream_cli.ema_tracker import SymbolEMA
from alpaca_stream_cli.macd_tracker import SymbolMACD, MACDResult
from alpaca_stream_cli.stochastic_tracker import SymbolStochastic, StochasticResult


# ---------------------------------------------------------------------------
# Colour helpers
# ---------------------------------------------------------------------------

def _rsi_color(value: float | None) -> str:
    """Return a Rich colour tag string based on RSI level."""
    if value is None:
        return "dim"
    if value >= 70:
        return "bold red"
    if value >= 60:
        return "yellow"
    if value <= 30:
        return "bold green"
    if value <= 40:
        return "cyan"
    return "white"


def _macd_color(result: MACDResult | None) -> str:
    """Return colour based on MACD histogram sign."""
    if result is None:
        return "dim"
    if result.histogram > 0:
        return "green"
    if result.histogram < 0:
        return "red"
    return "white"


def _stoch_color(result: StochasticResult | None) -> str:
    """Return colour based on Stochastic %K level."""
    if result is None:
        return "dim"
    if result.is_overbought:
        return "bold red"
    if result.is_oversold:
        return "bold green"
    return "white"


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def _fmt(value: float | None, decimals: int = 2) -> str:
    if value is None:
        return "--"
    return f"{value:.{decimals}f}"


def _fmt_macd(result: MACDResult | None) -> tuple[str, str, str]:
    """Return (macd_line, signal_line, histogram) as formatted strings."""
    if result is None:
        return "--", "--", "--"
    sign = "+" if result.histogram >= 0 else ""
    return (
        _fmt(result.macd_line),
        _fmt(result.signal_line),
        f"{sign}{result.histogram:.4f}",
    )


def _fmt_stoch(result: StochasticResult | None) -> tuple[str, str]:
    """Return (%K, %D) as formatted strings."""
    if result is None:
        return "--", "--"
    return _fmt(result.k), _fmt(result.d)


# ---------------------------------------------------------------------------
# Public builder
# ---------------------------------------------------------------------------

def build_indicator_table(
    symbols: Iterable[str],
    rsi_trackers: dict[str, SymbolRSI],
    ema_trackers: dict[str, SymbolEMA],
    macd_trackers: dict[str, SymbolMACD],
    stoch_trackers: dict[str, SymbolStochastic],
    *,
    title: str = "Technical Indicators",
) -> Table:
    """Build a Rich Table summarising key technical indicators per symbol.

    Parameters
    ----------
    symbols:
        Ordered iterable of ticker symbols to display.
    rsi_trackers:
        Mapping of uppercase symbol -> SymbolRSI instance.
    ema_trackers:
        Mapping of uppercase symbol -> SymbolEMA instance.
    macd_trackers:
        Mapping of uppercase symbol -> SymbolMACD instance.
    stoch_trackers:
        Mapping of uppercase symbol -> SymbolStochastic instance.
    title:
        Optional title for the table.
    """
    table = Table(
        title=title,
        box=box.SIMPLE_HEAD,
        show_lines=False,
        expand=False,
    )

    table.add_column("Symbol", style="bold cyan", no_wrap=True)
    table.add_column("RSI", justify="right")
    table.add_column("EMA", justify="right")
    table.add_column("MACD", justify="right")
    table.add_column("Signal", justify="right")
    table.add_column("Hist", justify="right")
    table.add_column("%K", justify="right")
    table.add_column("%D", justify="right")

    for raw_sym in symbols:
        sym = raw_sym.upper()

        rsi_obj = rsi_trackers.get(sym)
        rsi_val = rsi_obj.value() if rsi_obj is not None else None
        rsi_str = f"[{_rsi_color(rsi_val)}]{_fmt(rsi_val)}[/]"

        ema_obj = ema_trackers.get(sym)
        ema_val = ema_obj.value() if ema_obj is not None else None
        ema_str = _fmt(ema_val)

        macd_obj = macd_trackers.get(sym)
        macd_result = macd_obj.value() if macd_obj is not None else None
        macd_line_s, signal_s, hist_s = _fmt_macd(macd_result)
        mc = _macd_color(macd_result)
        macd_line_s = f"[{mc}]{macd_line_s}[/]"
        hist_s = f"[{mc}]{hist_s}[/]"

        stoch_obj = stoch_trackers.get(sym)
        stoch_result = stoch_obj.value() if stoch_obj is not None else None
        k_s, d_s = _fmt_stoch(stoch_result)
        sc = _stoch_color(stoch_result)
        k_s = f"[{sc}]{k_s}[/]"

        table.add_row(sym, rsi_str, ema_str, macd_line_s, signal_s, hist_s, k_s, d_s)

    return table
