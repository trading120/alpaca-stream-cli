"""Rich table display for funding rate estimates."""
from __future__ import annotations

from typing import Iterable

from rich.style import Style
from rich.table import Table

from alpaca_stream_cli.funding_rate import FundingRateResult, FundingRateTracker


def _rate_color(rate_pct: float | None) -> Style:
    if rate_pct is None:
        return Style(dim=True)
    if rate_pct > 0.10:
        return Style(color="bright_green", bold=True)
    if rate_pct > 0.02:
        return Style(color="green")
    if rate_pct < -0.10:
        return Style(color="bright_red", bold=True)
    if rate_pct < -0.02:
        return Style(color="red")
    return Style(color="white")


def _fmt_rate(rate_pct: float | None) -> str:
    if rate_pct is None:
        return "--"
    sign = "+" if rate_pct >= 0 else ""
    return f"{sign}{rate_pct:.4f}%"


def _fmt_label(label: str) -> str:
    colors = {"bullish": "green", "bearish": "red", "neutral": "white"}
    color = colors.get(label, "white")
    return f"[{color}]{label}[/{color}]"


def build_funding_rate_table(
    symbols: Iterable[str],
    tracker: FundingRateTracker,
) -> Table:
    table = Table(title="Funding Rate", expand=False, show_lines=False)
    table.add_column("Symbol", style="bold cyan", no_wrap=True)
    table.add_column("Rate", justify="right")
    table.add_column("Avg Dev", justify="right")
    table.add_column("Samples", justify="right")
    table.add_column("Bias", justify="center")

    for sym in symbols:
        result: FundingRateResult | None = tracker.get(sym)
        if result is None:
            table.add_row(sym.upper(), "--", "--", "--", "--")
            continue
        rate_style = _rate_color(result.rate_pct)
        table.add_row(
            result.symbol,
            f"[{rate_style}]{_fmt_rate(result.rate_pct)}[/]",
            _fmt_rate(result.avg_deviation),
            str(result.sample_count),
            _fmt_label(result.label),
        )
    return table
