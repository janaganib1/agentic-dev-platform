import argparse
import sys
from src.story1 import get_weather
from src.story2 import display_weather


def parse_args():
    parser = argparse.ArgumentParser(
        description="Get current weather for a city.",
        usage="py -m src.main <city>"
    )
    parser.add_argument(
        "city",
        nargs="?",
        help="City name to fetch weather for"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if not args.city:
        print("Usage: py -m src.main <city>")
        print("Example: py -m src.main Dallas")
        sys.exit(0)

    result = get_weather(args.city)

    if result is None:
        print(f"Error: Could not find weather for '{args.city}'.")
        print("Please check the city name and try again.")
        sys.exit(1)

    display_weather(result)


if __name__ == "__main__":
    main()