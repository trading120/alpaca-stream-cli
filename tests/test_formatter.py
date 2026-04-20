"""Tests for alpaca_stream_cli.formatter module."""

import pytest
from alpaca_stream_cli.formatter import (
    format_price,
    format_volume,
    format_percent,
    format_spread,
    color_for_change,
    format_price_change,
)


def test_format_price_normal():
    assert format_price(123.456) == "$123.46"


def test_format_price_none():
    assert format_price(None) == "--"


def test_format_price_custom_currency():
    assert format_price(10.0, currency="€") == "€10.00"


def test_format_volume_billions():
    assert format_volume(2_500_000_000) == "2.50B"


def test_format_volume_millions():
    assert format_volume(1_250_000) == "1.25M"


def test_format_volume_thousands():
    assert format_volume(5_500) == "5.5K"


def test_format_volume_small():
    assert format_volume(750) == "0.8K"


def test_format_volume_none():
    assert format_volume(None) == "--"


def test_format_percent_positive():
    result = format_percent(3.75)
    assert result == "+3.75%"


def test_format_percent_negative():
    result = format_percent(-1.5)
    assert result == "-1.50%"


def test_format_percent_no_sign():
    result = format_percent(2.0, include_sign=False)
    assert result == "2.00%"


def test_format_percent_none():
    assert format_percent(None) == "--"


def test_format_spread_normal():
    result = format_spread(100.0, 100.10)
    assert "$0.10" in result


def test_format_spread_none_bid():
    assert format_spread(None, 100.0) == "--"


def test_format_spread_none_ask():
    assert format_spread(100.0, None) == "--"


def test_color_for_change_positive():
    assert color_for_change(1.5) == "green"


def test_color_for_change_negative():
    assert color_for_change(-0.5) == "red"


def test_color_for_change_zero():
    assert color_for_change(0.0) == "white"


def test_color_for_change_none():
    assert color_for_change(None) == "white"


def test_format_price_change_gain():
    result = format_price_change(110.0, 100.0)
    assert result == "+10.00 (+10.00%)"


def test_format_price_change_loss():
    result = format_price_change(90.0, 100.0)
    assert result == "-10.00 (-10.00%)"


def test_format_price_change_none_inputs():
    assert format_price_change(None, 100.0) == "--"
    assert format_price_change(100.0, None) == "--"
    assert format_price_change(100.0, 0) == "--"
