from .config import CURRENCY_SYMBOL, DECIMAL_PLACES

def format_bitcoin_price(price: float) -> str:
    """Format Bitcoin price as USD currency with thousand separators."""
    return f"{CURRENCY_SYMBOL}{price:,.{DECIMAL_PLACES}f}"