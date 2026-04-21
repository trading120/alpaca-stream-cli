"""Integration layer: apply a SymbolFilter on top of a Watchlist."""
from __future__ import annotations

from typing import List, Optional

from alpaca_stream_cli.symbol_filter import SymbolFilter
from alpaca_stream_cli.watchlist import Watchlist


class WatchlistFilterIntegration:
    """Wraps a :class:`Watchlist` and exposes only symbols that pass a
    :class:`SymbolFilter`.

    This allows the rest of the application to work with a filtered view
    without mutating the underlying watchlist.
    """

    def __init__(
        self,
        watchlist: Watchlist,
        symbol_filter: Optional[SymbolFilter] = None,
    ) -> None:
        self._watchlist = watchlist
        self._filter = symbol_filter or SymbolFilter()

    # ------------------------------------------------------------------
    @property
    def filter(self) -> SymbolFilter:
        """The active :class:`SymbolFilter`."""
        return self._filter

    @filter.setter
    def filter(self, value: SymbolFilter) -> None:
        self._filter = value

    # ------------------------------------------------------------------
    def visible_symbols(self) -> List[str]:
        """Return watchlist symbols that pass the current filter."""
        return self._filter.apply(list(self._watchlist.symbols))

    def is_visible(self, symbol: str) -> bool:
        """Return True if *symbol* is in the watchlist **and** passes the filter."""
        return symbol.upper() in (
            s.upper() for s in self._watchlist.symbols
        ) and self._filter.matches(symbol)

    def hidden_symbols(self) -> List[str]:
        """Return watchlist symbols that are **blocked** by the current filter."""
        all_syms = list(self._watchlist.symbols)
        visible = set(self.visible_symbols())
        return [s for s in all_syms if s not in visible]

    # ------------------------------------------------------------------
    def set_include(self, patterns: List[str]) -> None:
        """Replace include patterns on the filter."""
        self._filter.include = list(patterns)
        self._filter._include_re = [
            __import__('alpaca_stream_cli.symbol_filter', fromlist=['_compile'])._compile(p)
            for p in patterns
        ]

    def set_exclude(self, patterns: List[str]) -> None:
        """Replace exclude patterns on the filter."""
        self._filter.exclude = list(patterns)
        self._filter._exclude_re = [
            __import__('alpaca_stream_cli.symbol_filter', fromlist=['_compile'])._compile(p)
            for p in patterns
        ]

    def reset_filter(self) -> None:
        """Clear all filter patterns — all watchlist symbols become visible."""
        self._filter.clear()
