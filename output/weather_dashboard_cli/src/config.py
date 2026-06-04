import os
from dotenv import load_dotenv

load_dotenv()

def get_api_key():
    """Returns weather API key from environment variables."""
    api_key = os.getenv('WEATHER_API_KEY')
    if not api_key:
        raise ValueError("WEATHER_API_KEY environment variable is required")
    return api_key

def get_api_url():
    """Returns weather API base URL from environment variables."""
    return os.getenv('WEATHER_API_URL', 'https://api.openweathermap.org/data/2.5/weather')