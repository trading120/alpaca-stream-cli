"""Wires AlertEngine output into AlertLog for persistent history."""

from __future__ import annotations

from typing import List

from alpaca_stream_cli.alert_log import AlertLog
from alpaca_stream_cli.alerts import AlertEngine, TriggeredAlert


class AlertLogIntegration:
    """Evaluates prices via AlertEngine and records triggers in AlertLog."""

    def __init__(
        self,
        engine: AlertEngine,
        log: AlertLog,
    ) -> None:
        self._engine = engine
        self._log = log

    def on_price(self, symbol: str, price: float) -> List[TriggeredAlert]:
        """Evaluate *price* for *symbol*; log and return any triggered alerts."""
        triggered = self._engine.evaluate(symbol, price)
        for alert in triggered:
            self._log.record(
                symbol=alert.symbol,
                condition=alert.condition,
                value=alert.value,
                threshold=alert.threshold,
            )
        return triggered

    def on_volume(self, symbol: str, volume: float) -> List[TriggeredAlert]:
        """Evaluate *volume* for *symbol*; log and return any triggered alerts."""
        triggered = self._engine.evaluate(symbol, volume, field="volume")
        for alert in triggered:
            self._log.record(
                symbol=alert.symbol,
                condition=alert.condition,
                value=alert.value,
                threshold=alert.threshold,
            )
        return triggered

    @property
    def log(self) -> AlertLog:
        return self._log

    def reset(self, symbol: str | None = None) -> None:
        """Reset engine state; optionally clear log entries for *symbol*."""
        self._engine.reset(symbol)
        if symbol is None:
            self._log.clear()
