# Weather Dashboard CLI

A simple command-line weather application that displays current weather information for any city.

## Setup

1. Clone or download the project
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Get a free API key from [OpenWeatherMap](https://openweathermap.org/api)

4. Create a `.env` file in the project root:
   ```bash
   cp .env.example .env
   ```

5. Edit `.env` and add your API key:
   ```
   WEATHER_API_KEY=your_actual_api_key_here
   WEATHER_API_URL=https://api.openweathermap.org/data/2.5/weather
   ```

## Usage

Run the weather dashboard with a city name:

```bash
# Examples
py -m src.main "Dallas"
py -m src.main "New York"
py -m src.main "London"
```

## Testing

Run tests with:
```bash
pytest tests/
```

## Features

- Current weather conditions
- Temperature in both Celsius and Fahrenheit
- Weather description
- Humidity percentage
- Wind speed
- Clean, formatted dashboard output