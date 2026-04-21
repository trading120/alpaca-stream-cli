"""Rate-limiting / throttle utilities for stream updates and alert notifications."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class ThrottleEntry:
    last_fired: float = 0.0
    fire_count: int = 0


class Throttle:
    """Prevents an event key from firing more often than *interval* seconds."""

    def __init__(self, interval: float = 1.0) -> None:
        if interval <= 0:
            raise ValueError("interval must be positive")
        self.interval = interval
        self._entries: Dict[str, ThrottleEntry] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def allow(self, key: str) -> bool:
        """Return True if *key* is allowed to fire right now.

        Calling this method records the attempt; successive calls within
        *interval* seconds for the same key will return False.
        """
        now = time.monotonic()
        entry = self._entries.get(key)
        if entry is None:
            self._entries[key] = ThrottleEntry(last_fired=now, fire_count=1)
            return True
        elapsed = now - entry.last_fired
        if elapsed >= self.interval:
            entry.last_fired = now
            entry.fire_count += 1
            return True
        return False

    def reset(self, key: str) -> None:
        """Clear throttle state for *key* so it can fire immediately."""
        self._entries.pop(key, None)

    def reset_all(self) -> None:
        """Clear all throttle state."""
        self._entries.clear()

    def fire_count(self, key: str) -> int:
        """Return how many times *key* has been allowed through."""
        entry = self._entries.get(key)
        return entry.fire_count if entry else 0

    def time_until_next(self, key: str) -> Optional[float]:
        """Seconds remaining before *key* may fire again, or None if ready."""
        entry = self._entries.get(key)
        if entry is None:
            return None
        remaining = self.interval - (time.monotonic() - entry.last_fired)
        return max(remaining, 0.0) if remaining > 0 else None
