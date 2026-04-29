"""Wires CorrelationTracker into the stream pipeline."""
from __future__ import annotations

from typing import List, Optional, Tuple

from alpaca_stream_cli.correlation_tracker import CorrelationResult, CorrelationTracker


class CorrelationIntegration:
    """Receives trade prices and exposes correlation results for display."""

    def __init__(
        self,
        symbols: Optional[List[str]] = None,
        window: int = 20,
        max_symbols: int = 50,
    ) -> None:
        self._tracker = CorrelationTracker(window=window, max_symbols=max_symbols)
        self._pinned_pairs: Optional[List[Tuple[str, str]]] = None
        if symbols and len(symbols) >= 2:
            syms = [s.upper() for s in symbols]
            self._pinned_pairs = [
                (syms[i], syms[j])
                for i in range(len(syms))
                for j in range(i + 1, len(syms))
            ]

    def on_trade(self, symbol: str, price: float) -> None:
        """Call this whenever a new trade price arrives."""
        try:
            self._tracker.record(symbol, price)
        except ValueError:
            pass  # silently drop bad prices

    def pairs(self) -> List[Tuple[str, str]]:
        """Return the pairs to display (pinned or all discovered)."""
        if self._pinned_pairs is not None:
            return self._pinned_pairs
        return self._tracker.pairs()

    def get(self, symbol_a: str, symbol_b: str) -> CorrelationResult:
        return self._tracker.correlation(symbol_a, symbol_b)

    def all_results(self) -> List[CorrelationResult]:
        return [self._tracker.correlation(a, b) for a, b in self.pairs()]

    @property
    def tracker(self) -> CorrelationTracker:
        return self._tracker
