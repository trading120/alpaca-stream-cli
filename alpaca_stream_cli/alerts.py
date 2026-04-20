"""Alert evaluation engine for price and volume thresholds."""

from dataclasses import dataclass
from typing import List, Optional, Callable
from alpaca_stream_cli.config import AlertConfig


@dataclass
class TriggeredAlert:
    symbol: str
    condition: str
    value: float


class AlertEngine:
    def __init__(self, alerts: List[AlertConfig], callback: Optional[Callable] = None):
        self._alerts = alerts
        self._callback = callback
        self._triggered: set = set()

    def evaluate(self, symbol: str, price: float, volume: int = 0) -> List[TriggeredAlert]:
        """Check all alerts for the given symbol against current market data."""
        fired: List[TriggeredAlert] = []

        for alert in self._alerts:
            if alert.symbol.upper() != symbol.upper():
                continue

            checks = []
            if alert.price_above is not None and price > alert.price_above:
                checks.append(TriggeredAlert(symbol, f"price > {alert.price_above}", price))
            if alert.price_below is not None and price < alert.price_below:
                checks.append(TriggeredAlert(symbol, f"price < {alert.price_below}", price))
            if alert.volume_above is not None and volume > alert.volume_above:
                checks.append(TriggeredAlert(symbol, f"volume > {alert.volume_above}", volume))

            for triggered in checks:
                key = (symbol, triggered.condition)
                if key not in self._triggered:
                    self._triggered.add(key)
                    fired.append(triggered)
                    if self._callback:
                        self._callback(triggered)

        return fired

    def reset(self, symbol: Optional[str] = None) -> None:
        """Clear triggered state, optionally for a specific symbol only."""
        if symbol:
            self._triggered = {k for k in self._triggered if k[0] != symbol.upper()}
        else:
            self._triggered.clear()
