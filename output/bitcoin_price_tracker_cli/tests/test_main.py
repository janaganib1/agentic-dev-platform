"""Tests for main module."""

from unittest.mock import patch
from src.main import format_usd_price, main


def test_format_usd_price():
    """Test USD price formatting."""
    result = format_usd_price(45123.45)
    assert result.startswith("$")
    assert "45" in result
    assert "123" in result


@patch('src.main.get_bitcoin_price')
def test_main_success(mock_get_price):
    """Test main function with successful price fetch."""
    mock_get_price.return_value = 50000.00
    try:
        main()
    except SystemExit:
        assert False, "main() should not exit on success"


@patch('src.main.get_bitcoin_price')
def test_main_failure(mock_get_price):
    """Test main function with failed price fetch."""
    mock_get_price.side_effect = Exception("API error")
    try:
        main()
        assert False, "main() should exit on error"
    except SystemExit as e:
        assert e.code == 1