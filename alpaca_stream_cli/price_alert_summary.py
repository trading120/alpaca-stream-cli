"""Aggregates triggered alerts into a per-symbol summary for display."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from alpaca_stream_cli.alert_log import AlertLog, AlertLogEntry


@dataclass
class SymbolAlertSummary:
    symbol: str
    total_triggers: int = 0
    last_price: Optional[float] = None
    last_condition: Optional[str] = None
    conditions_seen: List[str] = field(default_factory=list)

    def record(self, entry: AlertLogEntry) -> None:
        self.total_triggers += 1
        self.last_price = entry.price
        self.last_condition = entry.condition
        if entry.condition not in self.conditions_seen:
            self.conditions_seen.append(entry.condition)


class PriceAlertSummary:
    """Builds a per-symbol summary from an AlertLog."""

    def __init__(self, log: AlertLog) -> None:
        if not isinstance(log, AlertLog):
            raise TypeError("log must be an AlertLog instance")
        self._log = log

    def build(self) -> Dict[str, SymbolAlertSummary]:
        """Return a mapping of symbol -> SymbolAlertSummary."""
        summaries: Dict[str, SymbolAlertSummary] = {}
        for entry in self._log.entries():
            sym = entry.symbol.upper()
            if sym not in summaries:
                summaries[sym] = SymbolAlertSummary(symbol=sym)
            summaries[sym].record(entry)
        return summaries

    def for_symbol(self, symbol: str) -> Optional[SymbolAlertSummary]:
        """Return the summary for a single symbol, or None if not found."""
        return self.build().get(symbol.upper())

    def top_n(self, n: int = 5) -> List[SymbolAlertSummary]:
        """Return the top-n symbols by total trigger count, descending."""
        if n < 1:
            raise ValueError("n must be >= 1")
        summaries = self.build().values()
        return sorted(summaries, key=lambda s: s.total_triggers, reverse=True)[:n]
