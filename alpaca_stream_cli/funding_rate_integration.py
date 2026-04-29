"""Wires trade + quote events into the FundingRateTracker."""
from __future__ import annotations

from typing import Optional

from alpaca_stream_cli.funding_rate import FundingRateResult, FundingRateTracker


class FundingRateIntegration:
    """Listens to trade and quote events and feeds the funding rate tracker."""

    def __init__(self, window: int = 100, max_symbols: int = 200) -> None:
        self._tracker = FundingRateTracker(window=window, max_symbols=max_symbols)
        self._mids: dict[str, float] = {}

    def on_quote(self, symbol: str, bid: float, ask: float) -> None:
        """Update mid price from latest quote."""
        if bid > 0 and ask > 0:
            self._mids[symbol.upper()] = (bid + ask) / 2.0

    def on_trade(self, symbol: str, price: float) -> Optional[FundingRateResult]:
        """Record a trade and return updated funding rate if mid is known."""
        sym = symbol.upper()
        mid = self._mids.get(sym)
        if mid is None:
            return None
        return self._tracker.record(sym, price, mid)

    def get(self, symbol: str) -> Optional[FundingRateResult]:
        return self._tracker.get(symbol)

    def all_results(self) -> dict[str, FundingRateResult]:
        return self._tracker.all_results()

    @property
    def tracker(self) -> FundingRateTracker:
        return self._tracker
