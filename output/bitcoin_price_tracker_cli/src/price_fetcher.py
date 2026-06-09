"""Bitcoin price fetcher module."""

import urllib.request
import urllib.error
import json


COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"


def get_bitcoin_price() -> float:
    """Fetch current Bitcoin price in USD.

    Returns:
        float: Current Bitcoin price in USD

    Raises:
        Exception: If price fetch fails
    """
    try:
        # Use system proxy if available
        proxy_handler = urllib.request.ProxyHandler()
        opener = urllib.request.build_opener(proxy_handler)

        req = urllib.request.Request(
            COINGECKO_URL,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        with opener.open(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            return float(data["bitcoin"]["usd"])

    except Exception as e:
        raise Exception(f"Failed to fetch Bitcoin price: {e}")