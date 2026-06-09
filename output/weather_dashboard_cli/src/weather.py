import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("WEATHER_API_KEY")

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather(city: str) -> dict:
    response = requests.get(
        BASE_URL,
        params={"q": city, "appid": API_KEY, "units": "imperial"},
    )

    if response.status_code == 404:
        raise ValueError(f"City '{city}' not found")

    response.raise_for_status()

    data = response.json()

    return {
        "city": city,
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "wind_speed": data["wind"]["speed"],
        "description": data["weather"][0]["description"],
    }