# Weather CLI

Fetch and display current weather for any city using the OpenWeatherMap API.

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure your API key

Copy the example env file and fill in your key:
```bash
cp .env.example .env
```

Edit `.env` and replace `your_api_key_here` with your real key from [openweathermap.org](https://openweathermap.org/api).

## Usage

```bash
# Fetch weather for a city
py -m src.main Dallas
py -m src.main "New York"

# No argument — prints usage and exits automatically
py -m src.main

# Invalid city — prints error and exits with code 1
py -m src.main InvalidCity999
```

## Example Output

```
========================================
  Weather for Dallas, US
========================================
  Condition  : Clear sky
  Temperature: 91.2°F (feels like 94.1°F)
  Humidity   : 38%
  Wind Speed : 12.3 mph
========================================
```

## Run Tests

```bash
pytest tests/
```