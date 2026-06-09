# Project Summary: weather_dashboard_cli

**Generated:** 2026-06-08 19:51:40
**Complexity:** MEDIUM
**Original Requirement:** Develop a weather dashboard for a city name

Create a CLI application that accepts a city name
as input and displays the current weather conditions
including temperature, humidity, wind speed, and a
brief weather description.

Use the OpenWeatherMap API key from {{.ENV file WEATHER_API_KEY}}


Example usage: py -m src.main "Dallas"
**Project Summary:** A CLI application that accepts a city name and displays current weather conditions using the OpenWeatherMap API.
**Project Folder:** `output\weather_dashboard_cli`

---

## Stories Completed: 3/3

### Story 1: Fetch Weather Data — ✅ DONE

**Requirement:** Create a core module in src/weather.py that reads WEATHER_API_KEY from a .env file and fetches current weather data for a given city name from the OpenWeatherMap API, returning temperature, humidity, wind speed, and weather description as a dictionary.

**Acceptance Criteria:**
- Calling get_weather('Dallas') returns a dictionary with keys: city, temperature, humidity, wind_speed, and description
- The function reads WEATHER_API_KEY from the .env file using python-dotenv
- The function raises a clear exception when the city is not found

**QA Status:** PASS
**Tech Stack:** requests, python-dotenv, pytest

---

### Story 2: Format Weather Output — ✅ DONE

**Requirement:** Create a display module in src/display.py that accepts the weather dictionary and prints a formatted weather dashboard to the console showing all weather fields with labels and units.

**Acceptance Criteria:**
- Calling display_weather(weather_dict) prints city name, temperature in Celsius, humidity as percentage, wind speed in m/s, and weather description
- Output is human-readable with clear labels for each field

**QA Status:** PASS
**Tech Stack:** requests, python-dotenv, pytest

---

### Story 3: Build CLI Entry Point — ✅ DONE

**Requirement:** Create src/main.py as the CLI entry point that accepts a city name as a command-line argument, calls the weather fetch function, and passes the result to the display function.

**Acceptance Criteria:**
- Running py -m src.main 'Dallas' displays the formatted weather dashboard for Dallas without errors
- Running py -m src.main with no arguments prints a usage message and exits
- Running py -m src.main 'InvalidCity999' prints a clear error message and exits

**QA Status:** PASS
**Tech Stack:** requests, python-dotenv, pytest

---

## How to Run

```bash
cd output\weather_dashboard_cli
pip install -r requirements.txt
py -m src.main <your_arguments>
```

## Notes for Jira

- Total stories implemented: 3
- All stories are in folder: `output\weather_dashboard_cli`
- Each story's code is in `src/` subfolder
- Tests are in `tests/` subfolder
