"""Rich display helpers for sentiment scores."""
from __future__ import annotations

from typing import Dict

from rich.table import Table
from rich import box

from alpaca_stream_cli.news_sentiment import SentimentResult


def _score_color(score: float) -> str:
    if score >= 0.4:
        return "bold green"
    if score >= 0.1:
        return "green"
    if score <= -0.4:
        return "bold red"
    if score <= -0.1:
        return "red"
    return "white"


def _label_color(label: str) -> str:
    return {"Bullish": "green", "Bearish": "red"}.get(label, "white")


def _fmt_score(score: float) -> str:
    sign = "+" if score >= 0 else ""
    return f"{sign}{score:.3f}"


def _fmt_optional(val: float | None, decimals: int = 2) -> str:
    if val is None:
        return "[dim]—[/dim]"
    sign = "+" if val >= 0 else ""
    return f"{sign}{val:.{decimals}f}"


def build_sentiment_table(
    results: Dict[str, SentimentResult],
    title: str = "Market Sentiment",
) -> Table:
    table = Table(
        title=title,
        box=box.SIMPLE_HEAVY,
        show_header=True,
        header_style="bold cyan",
        expand=False,
    )
    table.add_column("Symbol", style="bold white", min_width=8)
    table.add_column("Score", justify="right", min_width=8)
    table.add_column("Sentiment", min_width=10)
    table.add_column("ROC %", justify="right", min_width=8)
    table.add_column("Rate/min", justify="right", min_width=9)

    for symbol, r in sorted(results.items()):
        color = _score_color(r.score)
        table.add_row(
            symbol,
            f"[{color}]{_fmt_score(r.score)}[/{color}]",
            f"[{_label_color(r.label)}]{r.label}[/{_label_color(r.label)}]",
            _fmt_optional(r.roc),
            _fmt_optional(r.trade_rate),
        )
    return table
