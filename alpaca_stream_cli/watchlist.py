"""Watchlist management: add, remove, and validate ticker symbols."""

import re
from typing import List

SYMBOL_PATTERN = re.compile(r"^[A-Z]{1,5}$")


class Watchlist:
    def __init__(self, symbols: List[str] = None):
        self._symbols: List[str] = []
        for sym in (symbols or []):
            self.add(sym)

    @staticmethod
    def validate(symbol: str) -> str:
        """Normalize and validate a ticker symbol."""
        symbol = symbol.strip().upper()
        if not SYMBOL_PATTERN.match(symbol):
            raise ValueError(
                f"Invalid symbol '{symbol}'. Must be 1-5 uppercase letters."
            )
        return symbol

    def add(self, symbol: str) -> bool:
        """Add a symbol. Returns True if added, False if already present."""
        symbol = self.validate(symbol)
        if symbol in self._symbols:
            return False
        self._symbols.append(symbol)
        return True

    def remove(self, symbol: str) -> bool:
        """Remove a symbol. Returns True if removed, False if not found."""
        symbol = symbol.strip().upper()
        if symbol in self._symbols:
            self._symbols.remove(symbol)
            return True
        return False

    def list(self) -> List[str]:
        """Return a copy of the current watchlist."""
        return list(self._symbols)

    def __len__(self) -> int:
        return len(self._symbols)

    def __contains__(self, symbol: str) -> bool:
        return symbol.strip().upper() in self._symbols

    def __repr__(self) -> str:
        return f"Watchlist({self._symbols})"
