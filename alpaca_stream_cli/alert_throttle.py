"""Alert-specific throttle integration: prevents alert spam by rate-limiting
per-symbol, per-condition alert notifications."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from alpaca_stream_cli.throttle import Throttle


@dataclass
class AlertThrottleConfig:
    """Configuration for alert throttling."""
    default_interval: float = 60.0  # seconds between repeated alerts
    per_symbol_overrides: dict[str, float] = field(default_factory=dict)


class AlertThrottle:
    """Rate-limits alert firing on a per-(symbol, condition) basis."""

    def __init__(self, config: Optional[AlertThrottleConfig] = None) -> None:
        self._config = config or AlertThrottleConfig()
        self._throttles: dict[str, Throttle] = {}

    def _key(self, symbol: str, condition: str) -> str:
        return f"{symbol.upper()}:{condition}"

    def _interval_for(self, symbol: str) -> float:
        return self._config.per_symbol_overrides.get(
            symbol.upper(), self._config.default_interval
        )

    def _get_throttle(self, symbol: str, condition: str) -> Throttle:
        key = self._key(symbol, condition)
        if key not in self._throttles:
            interval = self._interval_for(symbol)
            self._throttles[key] = Throttle(interval=interval)
        return self._throttles[key]

    def allow(self, symbol: str, condition: str) -> bool:
        """Return True if the alert for (symbol, condition) should fire."""
        return self._get_throttle(symbol, condition).allow()

    def reset(self, symbol: str, condition: str) -> None:
        """Manually reset throttle for a specific (symbol, condition)."""
        key = self._key(symbol, condition)
        if key in self._throttles:
            self._throttles[key].reset()

    def reset_symbol(self, symbol: str) -> None:
        """Reset all throttles associated with a symbol."""
        prefix = f"{symbol.upper()}:"
        for key in list(self._throttles):
            if key.startswith(prefix):
                self._throttles[key].reset()

    def active_keys(self) -> list[str]:
        """Return all active throttle keys."""
        return list(self._throttles.keys())
