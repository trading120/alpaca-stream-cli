"""Integrates PivotPointTracker with the OHLCV bar store."""
from __future__ import annotations

from typing import Dict, List, Optional

from alpaca_stream_cli.pivot_points import PivotPointTracker, PivotResult
from alpaca_stream_cli.ohlcv_bar import OHLCVBar


class PivotIntegration:
    """Keeps pivot levels in sync whenever a completed bar is available."""

    def __init__(self, max_symbols: int = 200) -> None:
        self._tracker = PivotPointTracker(max_symbols=max_symbols)
        self._last_bar: Dict[str, OHLCVBar] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def on_bar(self, bar: OHLCVBar) -> Optional[PivotResult]:
        """Feed a completed OHLCV bar; recompute pivots for that symbol.

        Returns the new PivotResult, or None if the bar was incomplete.
        """
        if bar.high is None or bar.low is None or bar.close is None:
            return None
        sym = bar.symbol.upper()
        try:
            result = self._tracker.update(
                sym,
                high=bar.high,
                low=bar.low,
                close=bar.close,
            )
        except (ValueError, OverflowError):
            return None
        self._last_bar[sym] = bar
        return result

    def get(self, symbol: str) -> Optional[PivotResult]:
        """Return the latest pivot levels for *symbol*, or None."""
        return self._tracker.get(symbol)

    def all_results(self, symbols: List[str]) -> Dict[str, Optional[PivotResult]]:
        """Return a mapping of symbol -> PivotResult for each requested symbol."""
        return {sym.upper(): self._tracker.get(sym) for sym in symbols}

    def remove(self, symbol: str) -> None:
        sym = symbol.upper()
        self._tracker.remove(sym)
        self._last_bar.pop(sym, None)

    def reset(self) -> None:
        self._tracker.clear()
        self._last_bar.clear()

    @property
    def tracker(self) -> PivotPointTracker:
        """Direct access to the underlying tracker (e.g. for display)."""
        return self._tracker
