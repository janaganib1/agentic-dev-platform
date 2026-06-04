import argparse
import sys
from .config import get_api_key, get_api_url
from .weather import fetch_weather_data, format_weather_dashboard

def parse_arguments():
    """Uses argparse to get city name from command line."""
    parser = argparse.ArgumentParser(description='Get weather information for a city')
    parser.add_argument('city', help='Name of the city to get weather for')
    return parser.parse_args()

def main():
    """Orchestrates the weather dashboard flow."""
    try:
        args = parse_arguments()
        weather_data = fetch_weather_data(args.city)
        dashboard = format_weather_dashboard(weather_data)
        print(dashboard)
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()