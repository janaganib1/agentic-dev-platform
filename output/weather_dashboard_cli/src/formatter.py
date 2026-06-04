from .config import get_default_units

def format_weather_data(weather_dict: dict) -> str:
    """Converts raw weather API response into readable dashboard string."""
    temperature = extract_temperature(weather_dict)
    humidity = extract_humidity(weather_dict)
    wind_speed = extract_wind_speed(weather_dict)
    weather_desc = extract_weather_description(weather_dict)
    
    dashboard = f"""
╔══════════════════════════════════════╗
║           WEATHER DASHBOARD          ║
╠══════════════════════════════════════╣
║ Temperature: {temperature:<22} ║
║ Humidity:    {humidity:<22} ║
║ Wind Speed:  {wind_speed:<22} ║
║ Condition:   {weather_desc:<22} ║
╚══════════════════════════════════════╝
""".strip()
    
    return dashboard

def extract_temperature(data: dict) -> str:
    """Extracts and formats temperature value."""
    temp_fields = ['temperature', 'temp', 'current_temperature']
    temperature = None
    
    for field in temp_fields:
        if field in data:
            temperature = data[field]
            break
    
    if temperature is None:
        return "N/A"
    
    units = get_default_units()
    symbol = "°C" if units.lower() == "celsius" else "°F"
    return f"{temperature}{symbol}"

def extract_humidity(data: dict) -> str:
    """Extracts and formats humidity percentage."""
    humidity_fields = ['humidity', 'relative_humidity', 'rh']
    
    for field in humidity_fields:
        if field in data:
            humidity = data[field]
            return f"{humidity}%"
    
    return "N/A"

def extract_wind_speed(data: dict) -> str:
    """Extracts and formats wind speed."""
    wind_fields = ['wind_speed', 'wind', 'windspeed']
    
    for field in wind_fields:
        if field in data:
            wind_speed = data[field]
            return f"{wind_speed} mph"
    
    return "N/A"

def extract_weather_description(data: dict) -> str:
    """Extracts weather condition description."""
    desc_fields = ['weather', 'description', 'condition', 'weather_description']
    
    for field in desc_fields:
        if field in data:
            description = data[field]
            return str(description).title()
    
    return "N/A"