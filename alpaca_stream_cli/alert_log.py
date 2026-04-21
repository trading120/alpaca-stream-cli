"""Persistent in-memory log of triggered alerts with bounded history."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Deque, Iterator, List, Optional

DEFAULT_MAX_ENTRIES = 100


@dataclass
class AlertLogEntry:
    symbol: str
    condition: str
    value: float
    threshold: float
    triggered_at: datetime = field(default_factory=datetime.utcnow)

    def __str__(self) -> str:
        ts = self.triggered_at.strftime("%H:%M:%S")
        return (
            f"[{ts}] {self.symbol} {self.condition} "
            f"value={self.value:.4f} threshold={self.threshold:.4f}"
        )


class AlertLog:
    """Bounded FIFO log of AlertLogEntry items."""

    def __init__(self, max_entries: int = DEFAULT_MAX_ENTRIES) -> None:
        if max_entries < 1:
            raise ValueError("max_entries must be >= 1")
        self._max_entries = max_entries
        self._entries: Deque[AlertLogEntry] = deque(maxlen=max_entries)

    def append(self, entry: AlertLogEntry) -> None:
        """Add a new entry to the log."""
        self._entries.append(entry)

    def record(
        self,
        symbol: str,
        condition: str,
        value: float,
        threshold: float,
        triggered_at: Optional[datetime] = None,
    ) -> AlertLogEntry:
        """Convenience factory: create and store an entry."""
        entry = AlertLogEntry(
            symbol=symbol.upper(),
            condition=condition,
            value=value,
            threshold=threshold,
            triggered_at=triggered_at or datetime.utcnow(),
        )
        self.append(entry)
        return entry

    def recent(self, n: int = 10) -> List[AlertLogEntry]:
        """Return the *n* most recent entries, newest last."""
        entries = list(self._entries)
        return entries[-n:] if n < len(entries) else entries

    def for_symbol(self, symbol: str) -> List[AlertLogEntry]:
        """Return all entries for *symbol* (case-insensitive)."""
        sym = symbol.upper()
        return [e for e in self._entries if e.symbol == sym]

    def clear(self) -> None:
        self._entries.clear()

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self) -> Iterator[AlertLogEntry]:
        return iter(self._entries)
