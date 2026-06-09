import requests
from src.config import API_KEY, BASE_URL


def get_weather(city: str) -> dict | None:
    if not API_KEY:
        return None
    try:
        response = requests.get(
            BASE_URL,
            params={"q": city, "appid": API_KEY, "units": "imperial"},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException:
        return None