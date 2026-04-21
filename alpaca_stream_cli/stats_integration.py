"""Integration helpers: wire SessionStats into StreamHandler updates."""

from typing import Optional

from alpaca_stream_cli.session_stats import SessionStats
from alpaca_stream_cli.snapshot_store import SnapshotStore


class StatsIntegration:
    """Bridges incoming trade data into SessionStats and SnapshotStore."""

    def __init__(
        self,
        session_stats: Optional[SessionStats] = None,
        snapshot_store: Optional[SnapshotStore] = None,
    ) -> None:
        self.session_stats = session_stats or SessionStats()
        self.snapshot_store = snapshot_store or SnapshotStore()

    def on_trade(self, symbol: str, price: float, volume: int = 0) -> None:
        """Record a trade event into session stats and update snapshot store."""
        sym = symbol.upper()
        self.session_stats.update(sym, price, volume)
        snap = self.snapshot_store.get(sym)
        if snap is not None:
            from dataclasses import replace
            updated = replace(snap, last=price)
            self.snapshot_store.update(sym, updated)

    def get_summary(self, symbol: str) -> dict:
        """Return a plain dict summary of session stats for a symbol."""
        s = self.session_stats.get(symbol)
        if s is None:
            return {}
        return {
            "symbol": s.symbol,
            "open": s.session_open,
            "high": s.high,
            "low": s.low,
            "last": s.last,
            "change_pct": s.session_change_pct,
            "volume": s.total_volume,
            "trades": s.trade_count,
        }

    def reset_symbol(self, symbol: str) -> None:
        self.session_stats.reset(symbol.upper())

    def reset_all(self) -> None:
        self.session_stats.reset_all()
