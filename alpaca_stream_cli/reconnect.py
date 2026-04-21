"""Reconnection policy with exponential backoff for the streaming connection."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class ReconnectPolicy:
    """Configuration for reconnection behaviour."""

    base_delay: float = 1.0
    max_delay: float = 60.0
    multiplier: float = 2.0
    max_attempts: int = 10
    jitter: float = 0.0  # seconds of random jitter to add (0 = disabled)


@dataclass
class ReconnectState:
    """Mutable state tracked across reconnection attempts."""

    attempts: int = 0
    last_attempt_at: Optional[float] = None
    _delays: list[float] = field(default_factory=list)

    def record_attempt(self, delay: float) -> None:
        self.attempts += 1
        self.last_attempt_at = time.monotonic()
        self._delays.append(delay)

    def reset(self) -> None:
        self.attempts = 0
        self.last_attempt_at = None
        self._delays.clear()


class ReconnectManager:
    """Manages reconnection attempts with exponential backoff."""

    def __init__(
        self,
        policy: Optional[ReconnectPolicy] = None,
        sleep_fn: Callable[[float], None] = time.sleep,
    ) -> None:
        self.policy = policy or ReconnectPolicy()
        self._sleep = sleep_fn
        self.state = ReconnectState()

    @property
    def exhausted(self) -> bool:
        """Return True when no more attempts are allowed."""
        return self.state.attempts >= self.policy.max_attempts

    def next_delay(self) -> float:
        """Compute the next backoff delay without advancing state."""
        import random

        delay = min(
            self.policy.base_delay * (self.policy.multiplier ** self.state.attempts),
            self.policy.max_delay,
        )
        if self.policy.jitter > 0:
            delay += random.uniform(0, self.policy.jitter)
        return delay

    def wait(self) -> bool:
        """Sleep for the next backoff interval.  Returns False if exhausted."""
        if self.exhausted:
            return False
        delay = self.next_delay()
        self.state.record_attempt(delay)
        self._sleep(delay)
        return True

    def reset(self) -> None:
        """Reset state after a successful connection."""
        self.state.reset()
