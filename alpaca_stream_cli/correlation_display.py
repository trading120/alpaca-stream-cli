"""Rich display helpers for correlation data."""
from __future__ import annotations

from typing import List, Optional, Tuple

from rich.table import Table
from rich import box
from rich.text import Text

from alpaca_stream_cli.correlation_tracker import CorrelationResult, CorrelationTracker


def _corr_color(corr: Optional[float]) -> str:
    if corr is None:
        return "dim"
    if corr >= 0.7:
        return "bold green"
    if corr >= 0.3:
        return "green"
    if corr >= -0.3:
        return "white"
    if corr >= -0.7:
        return "red"
    return "bold red"


def _fmt_corr(corr: Optional[float]) -> str:
    if corr is None:
        return "--"
    return f"{corr:+.3f}"


def _strength_label(corr: Optional[float]) -> str:
    if corr is None:
        return "--"
    a = abs(corr)
    if a >= 0.7:
        sign = "pos" if corr > 0 else "neg"
        return f"strong {sign}"
    if a >= 0.3:
        sign = "pos" if corr > 0 else "neg"
        return f"mild {sign}"
    return "neutral"


def build_correlation_table(
    tracker: CorrelationTracker,
    pairs: Optional[List[Tuple[str, str]]] = None,
    max_rows: int = 20,
) -> Table:
    table = Table(
        title="Correlation",
        box=box.SIMPLE_HEAVY,
        show_header=True,
        header_style="bold cyan",
        expand=False,
    )
    table.add_column("Symbol A", style="bold white", min_width=8)
    table.add_column("Symbol B", style="bold white", min_width=8)
    table.add_column("Correlation", justify="right", min_width=11)
    table.add_column("Strength", min_width=12)
    table.add_column("Samples", justify="right", min_width=7)

    target_pairs = pairs if pairs is not None else tracker.pairs()
    for a, b in target_pairs[:max_rows]:
        result = tracker.correlation(a, b)
        color = _corr_color(result.correlation)
        table.add_row(
            result.symbol_a,
            result.symbol_b,
            Text(_fmt_corr(result.correlation), style=color),
            Text(_strength_label(result.correlation), style=color),
            str(result.sample_count),
        )
    return table
