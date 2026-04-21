"""Alert dispatcher: evaluates alerts against live prices and dispatches
throttled notifications using AlertThrottle + AlertEngine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

from alpaca_stream_cli.alerts import AlertEngine, TriggeredAlert
from alpaca_stream_cli.alert_throttle import AlertThrottle, AlertThrottleConfig


NotifyCallback = Callable[[TriggeredAlert], None]


@dataclass
class DispatchResult:
    symbol: str
    dispatched: list[TriggeredAlert] = field(default_factory=list)
    suppressed: int = 0


class AlertDispatcher:
    """Combines AlertEngine evaluation with AlertThrottle gating.

    Only forwards alerts to the notify callback when the throttle permits.
    """

    def __init__(
        self,
        engine: AlertEngine,
        throttle_config: Optional[AlertThrottleConfig] = None,
        notify: Optional[NotifyCallback] = None,
    ) -> None:
        self._engine = engine
        self._throttle = AlertThrottle(config=throttle_config)
        self._notify = notify

    def set_notify(self, callback: NotifyCallback) -> None:
        """Register or replace the notification callback."""
        self._notify = callback

    def dispatch(self, symbol: str, price: float, volume: int = 0) -> DispatchResult:
        """Evaluate alerts for symbol and dispatch those not throttled.

        Args:
            symbol: Ticker symbol (case-insensitive).
            price: Current trade/quote price.
            volume: Cumulative volume for volume-based alerts.

        Returns:
            DispatchResult summarising dispatched and suppressed alerts.
        """
        triggered = self._engine.evaluate(symbol, price, volume)
        result = DispatchResult(symbol=symbol.upper())

        for alert in triggered:
            condition = alert.condition
            if self._throttle.allow(symbol, condition):
                result.dispatched.append(alert)
                if self._notify:
                    self._notify(alert)
            else:
                result.suppressed += 1

        return result

    def reset_symbol(self, symbol: str) -> None:
        """Reset throttle state for all conditions on a symbol."""
        self._throttle.reset_symbol(symbol)

    def reset_all(self) -> None:
        """Reset throttle state for every tracked (symbol, condition) pair."""
        for key in self._throttle.active_keys():
            sym, cond = key.split(":", 1)
            self._throttle.reset(sym, cond)
