"""Rich-based display helpers for session statistics."""

from typing import List
from rich.table import Table
from rich import box

from alpaca_stream_cli.session_stats import SessionStats, SymbolStats
from alpaca_stream_cli.formatter import format_price, format_volume, format_percent, color_for_change


def _fmt_optional_price(value) -> str:
    if value is None:
        return "[dim]--[/dim]"
    return format_price(value)


def _fmt_optional_pct(value) -> str:
    if value is None:
        return "[dim]--[/dim]"
    color = color_for_change(value)
    sign = "+" if value > 0 else ""
    return f"[{color}]{sign}{format_percent(value)}[/{color}]"


def build_stats_table(session_stats: SessionStats, symbols: List[str]) -> Table:
    """Build a Rich table showing per-symbol session statistics."""
    table = Table(
        title="Session Statistics",
        box=box.SIMPLE_HEAVY,
        show_header=True,
        header_style="bold cyan",
        expand=True,
    )
    table.add_column("Symbol", style="bold white", min_width=8)
    table.add_column("Open", justify="right")
    table.add_column("High", justify="right", style="green")
    table.add_column("Low", justify="right", style="red")
    table.add_column("Last", justify="right")
    table.add_column("Chg%", justify="right")
    table.add_column("Volume", justify="right")
    table.add_column("Trades", justify="right")

    for symbol in symbols:
        s: SymbolStats = session_stats.get(symbol)
        if s is None:
            table.add_row(
                symbol.upper(),
                "[dim]--[/dim]", "[dim]--[/dim]", "[dim]--[/dim]",
                "[dim]--[/dim]", "[dim]--[/dim]", "[dim]--[/dim]", "[dim]--[/dim]",
            )
        else:
            table.add_row(
                s.symbol,
                _fmt_optional_price(s.session_open),
                _fmt_optional_price(s.high),
                _fmt_optional_price(s.low),
                _fmt_optional_price(s.last),
                _fmt_optional_pct(s.session_change_pct),
                format_volume(s.total_volume),
                str(s.trade_count),
            )
    return table
