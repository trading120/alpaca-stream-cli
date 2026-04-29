"""Integration layer: wires stream trade messages into OrderFlowImbalanceTracker."""
from __future__ import annotations

from typing import Dict, List, Optional

from alpaca_stream_cli.order_flow_imbalance import OFIResult, OrderFlowImbalanceTracker


class OrderFlowIntegration:
    """Consumes raw trade dicts and feeds them to the OFI tracker.

    Side inference heuristic: compare trade price to last known mid-price.
    If no mid is available, fall back to the tape condition or default 'buy'.
    """

    def __init__(self, window: int = 100, max_symbols: int = 200) -> None:
        self._tracker = OrderFlowImbalanceTracker(
            window=window, max_symbols=max_symbols
        )
        self._last_mid: Dict[str, float] = {}

    def on_trade(self, symbol: str, price: float, volume: float) -> Optional[OFIResult]:
        """Record a trade and return the updated OFI result."""
        sym = symbol.upper()
        mid = self._last_mid.get(sym)
        if mid is None:
            side = "buy"
        elif price >= mid:
            side = "buy"
        else:
            side = "sell"
        try:
            return self._tracker.record(sym, price, volume, side)
        except RuntimeError:
            return None

    def on_quote(self, symbol: str, bid: float, ask: float) -> None:
        """Update the mid-price used for side inference."""
        if bid > 0 and ask > 0:
            self._last_mid[symbol.upper()] = (bid + ask) / 2.0

    def get(self, symbol: str) -> Optional[OFIResult]:
        return self._tracker.get(symbol)

    def symbols(self) -> List[str]:
        return self._tracker.symbols()
