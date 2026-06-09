import argparse
import sys
from src.weather import fetch_weather, display_weather


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch and display current weather for a city."
    )
    parser.add_argument("city", help="City name to fetch weather for (e.g. Dallas)")
    args = parser.parse_args()

    try:
        data = fetch_weather(args.city)
    except Exception as e:
        print(f"Error fetching weather: {e}")
        sys.exit(1)

    if data is None:
        print(f"Error: Could not find weather data for '{args.city}'. Check the city name and try again.")
        sys.exit(1)

    display_weather(data)


if __name__ == "__main__":
    main()