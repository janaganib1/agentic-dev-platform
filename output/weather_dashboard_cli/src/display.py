BORDER = "-----------------------------"

def display_weather(weather_dict: dict) -> None:
    city        = weather_dict["city"]
    temperature = weather_dict["temperature"]
    humidity    = weather_dict["humidity"]
    wind_speed  = weather_dict["wind_speed"]
    description = weather_dict["description"]

    print(BORDER)
    print(f" Weather Dashboard: {city}")
    print(BORDER)
    print(f" Temperature:  {temperature}°C")
    print(f" Humidity:     {humidity}%")
    print(f" Wind Speed:   {wind_speed} km/h")
    print(f" Description:  {description}")
    print(BORDER)