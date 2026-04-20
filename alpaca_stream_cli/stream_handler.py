"""Handles incoming Alpaca WebSocket stream messages and maintains quote state."""

from datetime import datetime
from typing import Callable, Dict, List, Optional

from alpaca_stream_cli.alerts import AlertEngine, TriggeredAlert
from alpaca_stream_cli.display import QuoteSnapshot, render_snapshot
from alpaca_stream_cli.watchlist import Watchlist


class StreamHandler:
    """Processes raw stream messages, updates state, and triggers rendering."""

    def __init__(
        self,
        watchlist: Watchlist,
        alert_engine: AlertEngine,
        on_render: Optional[Callable] = None,
    ) -> None:
        self.watchlist = watchlist
        self.alert_engine = alert_engine
        self._on_render = on_render or render_snapshot
        self._quotes: Dict[str, QuoteSnapshot] = {}
        self._prev_close: Dict[str, float] = {}

    def handle_message(self, msg: dict) -> None:
        """Dispatch a single stream message by type."""
        msg_type = msg.get("T")
        if msg_type == "q":
            self._handle_quote(msg)
        elif msg_type == "t":
            self._handle_trade(msg)

    def _handle_quote(self, msg: dict) -> None:
        symbol = msg.get("S", "").upper()
        if symbol not in self.watchlist.symbols:
            return
        existing = self._quotes.get(symbol)
        self._quotes[symbol] = QuoteSnapshot(
            symbol=symbol,
            bid=float(msg.get("bp", existing.bid if existing else 0.0)),
            ask=float(msg.get("ap", existing.ask if existing else 0.0)),
            last=existing.last if existing else 0.0,
            volume=existing.volume if existing else 0,
            change_pct=existing.change_pct if existing else None,
            timestamp=datetime.utcnow(),
        )
        self._refresh()

    def _handle_trade(self, msg: dict) -> None:
        symbol = msg.get("S", "").upper()
        if symbol not in self.watchlist.symbols:
            return
        price = float(msg.get("p", 0.0))
        volume = int(msg.get("s", 0))
        prev_close = self._prev_close.get(symbol)
        change_pct = ((price - prev_close) / prev_close * 100) if prev_close else None

        existing = self._quotes.get(symbol)
        self._quotes[symbol] = QuoteSnapshot(
            symbol=symbol,
            bid=existing.bid if existing else 0.0,
            ask=existing.ask if existing else 0.0,
            last=price,
            volume=(existing.volume if existing else 0) + volume,
            change_pct=change_pct,
            timestamp=datetime.utcnow(),
        )
        self._refresh()

    def set_prev_close(self, symbol: str, price: float) -> None:
        self._prev_close[symbol.upper()] = price

    def _refresh(self) -> None:
        snapshots = [self._quotes[s] for s in self.watchlist.symbols if s in self._quotes]
        triggered: List[TriggeredAlert] = []
        for snap in snapshots:
            triggered.extend(self.alert_engine.evaluate(snap.symbol, snap.last, snap.volume))
        self._on_render(snapshots, triggered)

    @property
    def quotes(self) -> Dict[str, QuoteSnapshot]:
        return dict(self._quotes)
