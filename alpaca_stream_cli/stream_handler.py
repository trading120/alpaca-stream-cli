"""Handles raw Alpaca stream messages and keeps the SnapshotStore up to date."""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Optional

from alpaca_stream_cli.alerts import AlertEngine, TriggeredAlert
from alpaca_stream_cli.display import QuoteSnapshot
from alpaca_stream_cli.snapshot_store import SnapshotStore
from alpaca_stream_cli.watchlist import Watchlist

log = logging.getLogger(__name__)

OnAlertCallback = Callable[[TriggeredAlert], None]


class StreamHandler:
    """Processes incoming websocket messages from Alpaca's data stream."""

    def __init__(
        self,
        watchlist: Watchlist,
        alert_engine: AlertEngine,
        store: Optional[SnapshotStore] = None,
        on_alert: Optional[OnAlertCallback] = None,
    ) -> None:
        self.watchlist = watchlist
        self.alert_engine = alert_engine
        self.store: SnapshotStore = store if store is not None else SnapshotStore()
        self.on_alert = on_alert
        # Accumulate intra-session volume per symbol
        self._volume: Dict[str, int] = {}

    # ------------------------------------------------------------------
    # Public entry-point
    # ------------------------------------------------------------------

    def handle_message(self, msg: Dict[str, Any]) -> None:
        """Dispatch a single decoded message dict."""
        msg_type = msg.get("T")
        if msg_type == "t":
            self._handle_trade(msg)
        elif msg_type == "q":
            self._handle_quote(msg)
        else:
            log.debug("Unhandled message type: %s", msg_type)

    # ------------------------------------------------------------------
    # Internal handlers
    # ------------------------------------------------------------------

    def _handle_trade(self, msg: Dict[str, Any]) -> None:
        symbol: str = msg.get("S", "").upper()
        if symbol not in self.watchlist:
            return

        price: float = float(msg.get("p", 0.0))
        size: int = int(msg.get("s", 0))

        self._volume[symbol] = self._volume.get(symbol, 0) + size

        existing = self.store.get(symbol)
        if existing is not None:
            prev = existing.last or price
            change = price - prev
            change_pct = (change / prev * 100.0) if prev else 0.0
            updated = QuoteSnapshot(
                symbol=symbol,
                bid=existing.bid,
                ask=existing.ask,
                last=price,
                change=change,
                change_pct=change_pct,
                volume=self._volume[symbol],
            )
        else:
            updated = QuoteSnapshot(
                symbol=symbol,
                bid=None,
                ask=None,
                last=price,
                change=0.0,
                change_pct=0.0,
                volume=self._volume[symbol],
            )
        self.store.update(updated)
        self._fire_alerts(symbol, price, self._volume[symbol])

    def _handle_quote(self, msg: Dict[str, Any]) -> None:
        symbol: str = msg.get("S", "").upper()
        if symbol not in self.watchlist:
            return

        bid: float = float(msg.get("bp", 0.0))
        ask: float = float(msg.get("ap", 0.0))

        existing = self.store.get(symbol)
        if existing is not None:
            updated = QuoteSnapshot(
                symbol=symbol,
                bid=bid,
                ask=ask,
                last=existing.last,
                change=existing.change,
                change_pct=existing.change_pct,
                volume=existing.volume,
            )
        else:
            updated = QuoteSnapshot(
                symbol=symbol,
                bid=bid,
                ask=ask,
                last=None,
                change=0.0,
                change_pct=0.0,
                volume=0,
            )
        self.store.update(updated)

    # ------------------------------------------------------------------
    # Alert helpers
    # ------------------------------------------------------------------

    def _fire_alerts(self, symbol: str, price: float, volume: int) -> None:
        triggered = self.alert_engine.evaluate(symbol, price, volume)
        if triggered and self.on_alert:
            for alert in triggered:
                self.on_alert(alert)
