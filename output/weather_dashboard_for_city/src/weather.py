import requests
from .config import API_KEY


def fetch_weather(city: str) -> dict | None:
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "imperial",
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 404:
            return None
        if response.status_code != 200:
            return None
        raw = response.json()
        return {
            "city": raw["name"],
            "country": raw["sys"]["country"],
            "temp": raw["main"]["temp"],
            "feels_like": raw["main"]["feels_like"],
            "humidity": raw["main"]["humidity"],
            "description": raw["weather"][0]["description"].capitalize(),
            "wind_speed": raw["wind"]["speed"],
        }
    except Exception:
        return None


def display_weather(data: dict) -> None:
    print("=" * 40)
    print(f"  Weather for {data['city']}, {data['country']}")
    print("=" * 40)
    print(f"  Condition  : {data['description']}")
    print(f"  Temperature: {data['temp']}°F (feels like {data['feels_like']}°F)")
    print(f"  Humidity   : {data['humidity']}%")
    print(f"  Wind Speed : {data['wind_speed']} mph")
    print("=" * 40)