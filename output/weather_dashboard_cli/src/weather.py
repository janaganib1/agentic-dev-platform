import requests
import json
from .config import get_api_key, get_api_url

def fetch_weather_data(city: str):
    """Calls weather API and returns raw JSON data."""
    api_key = get_api_key()
    api_url = get_api_url()
    
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric'
    }
    
    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch weather data: {str(e)}")

def format_weather_dashboard(weather_data: dict):
    """Formats weather data into readable dashboard string."""
    city = weather_data['name']
    country = weather_data['sys']['country']
    temp_c = weather_data['main']['temp']
    temp_f = (temp_c * 9/5) + 32
    description = weather_data['weather'][0]['description'].title()
    humidity = weather_data['main']['humidity']
    wind_speed = weather_data['wind']['speed']
    
    dashboard = f"""
═══════════════════════════════════
          WEATHER DASHBOARD
═══════════════════════════════════
City:         {city}, {country}
Temperature:  {temp_c:.1f}°C ({temp_f:.1f}°F)
Description:  {description}
Humidity:     {humidity}%
Wind Speed:   {wind_speed} m/s
═══════════════════════════════════
"""
    return dashboard.strip()