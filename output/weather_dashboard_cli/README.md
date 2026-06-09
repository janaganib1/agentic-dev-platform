# Weather CLI

A command-line tool to fetch and display current weather for any city using the OpenWeatherMap API.

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your WEATHER_API_KEY
   ```

## Run Commands

```bash
# Normal usage — prints formatted weather dashboard
py -m src.main Dallas

# No argument — prints usage message, exits cleanly
py -m src.main

# Invalid city — prints user-friendly error message
py -m src.main FakeCity123
```

## Run Tests

```bash
pytest tests/test_main.py
```

## Environment Variables

| Variable | Description | Example |
|---|---|---|
| `WEATHER_API_KEY` | OpenWeatherMap API key | `abc123def456` |
| `WEATHER_BASE_URL` | Base URL for weather API | `https://api.openweathermap.org/data/2.5/weather` |

Get a free API key at https://openweathermap.org/api