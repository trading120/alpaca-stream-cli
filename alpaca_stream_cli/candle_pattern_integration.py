"""Integration layer: feeds OHLCV bars into the candle pattern tracker."""
from __future__ import annotations
from typing import Optional
from alpaca_stream_cli.candle_pattern import CandlePatternTracker, PatternResult
from alpaca_stream_cli.ohlcv_bar import OHLCVBar


class CandlePatternIntegration:
    """Wraps CandlePatternTracker and wires it to bar events."""

    def __init__(self) -> None:
        self._tracker = CandlePatternTracker()

    def on_bar(self, bar: OHLCVBar) -> PatternResult:
        """Process a completed OHLCV bar and return the detected pattern."""
        return self._tracker.record(bar)

    def get(self, symbol: str) -> Optional[PatternResult]:
        """Return the latest pattern result for *symbol*."""
        return self._tracker.get(symbol)

    def all_results(self) -> list[PatternResult]:
        """Return pattern results for all tracked symbols."""
        return self._tracker.all_results()

    @property
    def tracker(self) -> CandlePatternTracker:
        return self._tracker
