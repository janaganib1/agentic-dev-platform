import requests
from .config import get_api_key

def get_weather(city_name: str) -> dict:
    """Fetches weather data for given city and returns formatted dictionary."""
    api_key = get_api_key()
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city_name,
        'appid': api_key,
        'units': 'metric'
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    response_data = response.json()
    return parse_weather_response(response_data)

def parse_weather_response(response_data: dict) -> dict:
    """Extracts required fields from API response."""
    return {
        "temperature": float(response_data['main']['temp']),
        "humidity": int(response_data['main']['humidity']),
        "wind_speed": float(response_data['wind']['speed']),
        "description": str(response_data['weather'][0]['description'])
    }