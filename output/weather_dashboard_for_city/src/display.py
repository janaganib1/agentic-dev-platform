def display_weather(weather_dict: dict) -> None:
    city        = weather_dict["city"]
    temperature = weather_dict["temperature"]
    humidity    = weather_dict["humidity"]
    wind_speed  = weather_dict["wind_speed"]
    description = weather_dict["description"]

    print("=" * 30)
    print(f"{'City:':<13}{city}")
    print(f"{'Temperature:':<13}{temperature} °C")
    print(f"{'Humidity:':<13}{humidity}%")
    print(f"{'Wind Speed:':<13}{wind_speed} m/s")
    print(f"{'Description:':<13}{description}")
    print("=" * 30)