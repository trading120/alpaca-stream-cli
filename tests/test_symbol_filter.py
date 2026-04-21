"""Tests for alpaca_stream_cli.symbol_filter."""
import pytest

from alpaca_stream_cli.symbol_filter import SymbolFilter, filter_symbols


SYMBOLS = ["AAPL", "AMZN", "GOOG", "MSFT", "META", "TSLA", "NVDA"]


# ---------------------------------------------------------------------------
# filter_symbols convenience wrapper
# ---------------------------------------------------------------------------

def test_no_filters_returns_all():
    assert filter_symbols(SYMBOLS) == SYMBOLS


def test_include_exact_match():
    result = filter_symbols(SYMBOLS, include=["AAPL"])
    assert result == ["AAPL"]


def test_include_wildcard():
    result = filter_symbols(SYMBOLS, include=["A*"])
    assert set(result) == {"AAPL", "AMZN"}


def test_exclude_exact_match():
    result = filter_symbols(SYMBOLS, exclude=["TSLA"])
    assert "TSLA" not in result
    assert len(result) == len(SYMBOLS) - 1


def test_exclude_wildcard():
    result = filter_symbols(SYMBOLS, exclude=["M*"])
    assert "MSFT" not in result
    assert "META" not in result


def test_include_and_exclude_combined():
    # include everything starting with A, but exclude AMZN
    result = filter_symbols(SYMBOLS, include=["A*"], exclude=["AMZN"])
    assert result == ["AAPL"]


def test_case_insensitive_pattern():
    result = filter_symbols(SYMBOLS, include=["aapl"])
    assert result == ["AAPL"]


def test_case_insensitive_symbol():
    result = filter_symbols(["aapl", "tsla"], include=["AAPL"])
    assert result == ["aapl"]


# ---------------------------------------------------------------------------
# SymbolFilter class
# ---------------------------------------------------------------------------

def test_matches_with_no_patterns():
    f = SymbolFilter()
    assert f.matches("AAPL") is True


def test_matches_include_passes():
    f = SymbolFilter(include=["AAPL"])
    assert f.matches("AAPL") is True
    assert f.matches("GOOG") is False


def test_matches_exclude_blocks():
    f = SymbolFilter(exclude=["TSLA"])
    assert f.matches("TSLA") is False
    assert f.matches("AAPL") is True


def test_add_include_at_runtime():
    f = SymbolFilter()
    f.add_include("NV*")
    assert f.matches("NVDA") is True
    assert f.matches("AAPL") is False


def test_add_exclude_at_runtime():
    f = SymbolFilter()
    f.add_exclude("GOOG")
    assert f.matches("GOOG") is False
    assert f.matches("AAPL") is True


def test_clear_removes_all_patterns():
    f = SymbolFilter(include=["AAPL"], exclude=["TSLA"])
    f.clear()
    assert f.matches("AAPL") is True
    assert f.matches("TSLA") is True


def test_apply_preserves_order():
    f = SymbolFilter(include=["A*", "G*"])
    result = f.apply(SYMBOLS)
    assert result == ["AAPL", "AMZN", "GOOG"]


def test_wildcard_matches_any():
    f = SymbolFilter(include=["*"])
    assert f.apply(SYMBOLS) == SYMBOLS
