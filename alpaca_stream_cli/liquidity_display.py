"""Rich display helpers for the liquidity score tracker."""
from __future__ import annotations

from typing import Sequence

from rich.table import Table
from rich import box

from alpaca_stream_cli.liquidity_score import LiquidityResult, LiquidityScoreTracker


def _score_color(score: float) -> str:
    if score >= 0.75:
        return "bold green"
    if score >= 0.40:
        return "yellow"
    return "bold red"


def _label_color(label: str) -> str:
    return {"HIGH": "green", "MED": "yellow", "LOW": "red"}.get(label, "white")


def _bar(value: float, width: int = 10) -> str:
    """Simple ASCII progress bar for a 0-1 normalised value."""
    filled = round(value * width)
    return "[" + "█" * filled + "░" * (width - filled) + "]"


def _fmt(value: float) -> str:
    return f"{value:.3f}"


def build_liquidity_table(
    tracker: LiquidityScoreTracker,
    symbols: Sequence[str],
) -> Table:
    table = Table(
        title="Liquidity Scores",
        box=box.SIMPLE_HEAD,
        show_lines=False,
        expand=False,
    )
    table.add_column("Symbol", style="bold white", no_wrap=True)
    table.add_column("Score", justify="right")
    table.add_column("Label", justify="center")
    table.add_column("Bar", justify="left")
    table.add_column("Spread", justify="right")
    table.add_column("Volume", justify="right")
    table.add_column("Rate", justify="right")

    for sym in symbols:
        result = tracker.get(sym)
        if result is None:
            table.add_row(
                sym.upper(), "—", "—", "—", "—", "—", "—"
            )
            continue
        color = _score_color(result.score)
        lcolor = _label_color(result.label)
        table.add_row(
            result.symbol,
            f"[{color}]{_fmt(result.score)}[/{color}]",
            f"[{lcolor}]{result.label}[/{lcolor}]",
            _bar(result.score),
            _fmt(result.spread_component),
            _fmt(result.volume_component),
            _fmt(result.rate_component),
        )
    return table
