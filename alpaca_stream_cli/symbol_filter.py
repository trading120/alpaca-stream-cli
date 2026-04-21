"""Symbol filter: pattern-based filtering for watchlist symbols."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SymbolFilter:
    """Filter symbols by inclusion/exclusion patterns.

    Patterns are case-insensitive prefix strings or simple glob-style
    wildcards (``*`` matches any sequence of characters).
    """

    include: List[str] = field(default_factory=list)
    exclude: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._include_re = [_compile(p) for p in self.include]
        self._exclude_re = [_compile(p) for p in self.exclude]

    # ------------------------------------------------------------------
    def matches(self, symbol: str) -> bool:
        """Return True if *symbol* passes the filter."""
        s = symbol.upper()
        if self._exclude_re and any(r.fullmatch(s) for r in self._exclude_re):
            return False
        if self._include_re and not any(r.fullmatch(s) for r in self._include_re):
            return False
        return True

    def apply(self, symbols: List[str]) -> List[str]:
        """Return the subset of *symbols* that pass the filter, preserving order."""
        return [s for s in symbols if self.matches(s)]

    # ------------------------------------------------------------------
    def add_include(self, pattern: str) -> None:
        """Append an inclusion pattern at runtime."""
        self.include.append(pattern)
        self._include_re.append(_compile(pattern))

    def add_exclude(self, pattern: str) -> None:
        """Append an exclusion pattern at runtime."""
        self.exclude.append(pattern)
        self._exclude_re.append(_compile(pattern))

    def clear(self) -> None:
        """Remove all patterns."""
        self.include.clear()
        self.exclude.clear()
        self._include_re.clear()
        self._exclude_re.clear()


# ---------------------------------------------------------------------------
def _compile(pattern: str) -> re.Pattern[str]:
    """Compile a glob-style pattern to a regex (case-insensitive)."""
    escaped = re.escape(pattern.upper()).replace(r"\*", ".*")
    return re.compile(escaped, re.IGNORECASE)


def filter_symbols(
    symbols: List[str],
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
) -> List[str]:
    """Convenience wrapper — filter *symbols* without constructing a class."""
    f = SymbolFilter(include=include or [], exclude=exclude or [])
    return f.apply(symbols)
