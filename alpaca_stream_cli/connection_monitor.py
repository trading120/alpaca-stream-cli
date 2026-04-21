"""Tracks stream connection health and surfaces status for the UI."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class ConnectionStatus(str, Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    FAILED = "failed"


@dataclass
class ConnectionEvent:
    status: ConnectionStatus
    timestamp: float = field(default_factory=time.monotonic)
    message: str = ""


class ConnectionMonitor:
    """Records connection lifecycle events and exposes current state."""

    def __init__(self, max_events: int = 50) -> None:
        if max_events < 1:
            raise ValueError("max_events must be at least 1")
        self._max_events = max_events
        self._events: list[ConnectionEvent] = []
        self._status: ConnectionStatus = ConnectionStatus.DISCONNECTED
        self._connected_at: Optional[float] = None
        self.reconnect_count: int = 0

    @property
    def status(self) -> ConnectionStatus:
        return self._status

    @property
    def is_connected(self) -> bool:
        return self._status == ConnectionStatus.CONNECTED

    @property
    def uptime(self) -> Optional[float]:
        """Seconds since last successful connection, or None if not connected."""
        if self._connected_at is None or not self.is_connected:
            return None
        return time.monotonic() - self._connected_at

    def _record(self, status: ConnectionStatus, message: str = "") -> ConnectionEvent:
        event = ConnectionEvent(status=status, message=message)
        self._events.append(event)
        if len(self._events) > self._max_events:
            self._events.pop(0)
        self._status = status
        return event

    def on_connecting(self, message: str = "") -> None:
        self._record(ConnectionStatus.CONNECTING, message)

    def on_connected(self, message: str = "") -> None:
        self._connected_at = time.monotonic()
        self._record(ConnectionStatus.CONNECTED, message)

    def on_disconnected(self, message: str = "") -> None:
        self._connected_at = None
        self._record(ConnectionStatus.DISCONNECTED, message)

    def on_reconnecting(self, message: str = "") -> None:
        self.reconnect_count += 1
        self._record(ConnectionStatus.RECONNECTING, message)

    def on_failed(self, message: str = "") -> None:
        self._connected_at = None
        self._record(ConnectionStatus.FAILED, message)

    def events(self) -> list[ConnectionEvent]:
        """Return a copy of recorded events, oldest first."""
        return list(self._events)

    def reset(self) -> None:
        self._events.clear()
        self._status = ConnectionStatus.DISCONNECTED
        self._connected_at = None
        self.reconnect_count = 0
