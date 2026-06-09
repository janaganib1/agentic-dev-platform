"""CLI entry point for Bitcoin price display."""

import locale
import sys
from .config import CURRENCY_LOCALE
from .price_fetcher import get_bitcoin_price


def format_usd_price(price: float) -> str:
    """Format price as USD currency string.
    
    Args:
        price: Price value as float
        
    Returns:
        str: Formatted price string like "$45,123.45"
    """
    try:
        locale.setlocale(locale.LC_ALL, CURRENCY_LOCALE)
        return locale.currency(price, grouping=True)
    except locale.Error:
        # Fallback to simple string formatting if locale setting fails
        return f"${price:,.2f}"


def main() -> None:
    """Main CLI entry point."""
    try:
        price = get_bitcoin_price()
        formatted_price = format_usd_price(price)
        print(f"Current Bitcoin Price: {formatted_price}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()