import requests
import json
from .config import get_api_timeout

def get_bitcoin_price() -> float:
    """Fetches Bitcoin price from CoinGecko API and returns USD price as float."""
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    timeout = get_api_timeout()
    
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        price = data['bitcoin']['usd']
        return float(price)
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch Bitcoin price: {e}")
    except (KeyError, ValueError, json.JSONDecodeError) as e:
        raise Exception(f"Failed to parse Bitcoin price from response: {e}")