"""Rich display table for candlestick pattern results."""
from __future__ import annotations
from typing import Optional
from rich.table import Table
from rich.text import Text
from alpaca_stream_cli.candle_pattern import CandlePatternTracker, PatternResult

_PATTERN_LABELS: dict[str, str] = {
    "doji": "Doji",
    "hammer": "Hammer",
    "shooting_star": "Shooting Star",
    "marubozu": "Marubozu",
}


def _pattern_color(result: Optional[PatternResult]) -> str:
    if result is None or result.pattern is None:
        return "dim"
    if result.bullish is True:
        return "green"
    if result.bullish is False:
        return "red"
    return "yellow"


def _fmt_pattern(result: Optional[PatternResult]) -> Text:
    if result is None or result.pattern is None:
        return Text("—", style="dim")
    label = _PATTERN_LABELS.get(result.pattern, result.pattern)
    color = _pattern_color(result)
    return Text(label, style=color)


def _fmt_direction(result: Optional[PatternResult]) -> Text:
    if result is None or result.bullish is None:
        return Text("—", style="dim")
    if result.bullish:
        return Text("▲ Bullish", style="bold green")
    return Text("▼ Bearish", style="bold red")


def build_candle_pattern_table(
    tracker: CandlePatternTracker,
    symbols: list[str],
) -> Table:
    table = Table(title="Candlestick Patterns", expand=False)
    table.add_column("Symbol", style="bold white", width=8)
    table.add_column("Pattern", width=14)
    table.add_column("Direction", width=12)

    for sym in symbols:
        result = tracker.get(sym)
        table.add_row(
            sym.upper(),
            _fmt_pattern(result),
            _fmt_direction(result),
        )
    return table
