"""In-memory store for the latest QuoteSnapshot per symbol."""

from __future__ import annotations

from threading import Lock
from typing import Dict, Iterator, List, Optional

from alpaca_stream_cli.display import QuoteSnapshot


class SnapshotStore:
    """Thread-safe store that holds the most recent QuoteSnapshot for each symbol."""

    def __init__(self) -> None:
        self._snapshots: Dict[str, QuoteSnapshot] = {}
        self._lock = Lock()

    # ------------------------------------------------------------------
    # Mutations
    # ------------------------------------------------------------------

    def update(self, snapshot: QuoteSnapshot) -> None:
        """Insert or replace the snapshot for *snapshot.symbol*."""
        key = snapshot.symbol.upper()
        with self._lock:
            self._snapshots[key] = snapshot

    def remove(self, symbol: str) -> bool:
        """Remove a symbol from the store.  Returns True if it existed."""
        key = symbol.upper()
        with self._lock:
            if key in self._snapshots:
                del self._snapshots[key]
                return True
            return False

    def clear(self) -> None:
        """Remove all snapshots."""
        with self._lock:
            self._snapshots.clear()

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get(self, symbol: str) -> Optional[QuoteSnapshot]:
        """Return the snapshot for *symbol*, or None if not present."""
        return self._snapshots.get(symbol.upper())

    def all(self) -> List[QuoteSnapshot]:
        """Return a stable list of all snapshots, sorted by symbol."""
        with self._lock:
            return sorted(self._snapshots.values(), key=lambda s: s.symbol)

    def symbols(self) -> List[str]:
        """Return sorted list of tracked symbols."""
        with self._lock:
            return sorted(self._snapshots.keys())

    def __len__(self) -> int:
        return len(self._snapshots)

    def __iter__(self) -> Iterator[QuoteSnapshot]:
        return iter(self.all())

    def __contains__(self, symbol: object) -> bool:
        if not isinstance(symbol, str):
            return False
        return symbol.upper() in self._snapshots
