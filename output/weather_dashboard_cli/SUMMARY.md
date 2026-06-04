# Project Summary: weather_dashboard_cli

**Generated:** 2026-06-04 17:01:41
**Complexity:** MEDIUM
**Original Requirement:** Develop a weather dashboard for a city name

Create a CLI application that accepts a city name as input and displays the current weather conditions including temperature, humidity, wind speed, and a brief weather description. Use the OpenWeatherMap API key from  .ENV file WEATHER_API_KEY Example usage: py -m src.main "Dallas"
**Project Summary:** A CLI application that fetches and displays current weather conditions for a specified city using the OpenWeatherMap API.
**Project Folder:** `output\weather_dashboard_cli`

---

## Stories Completed: 3/3

### Story 1: Weather API Client — ✅ DONE

**Requirement:** Create a weather service module that fetches current weather data from OpenWeatherMap API using city name and API key from environment variables.

**Acceptance Criteria:**
- Core function returns weather data dict with temperature, humidity, wind speed, and description for valid city input

**QA Status:** PASS
**Tech Stack:** requests, python-dotenv, pytest

---

### Story 2: Weather Data Formatter — ✅ DONE

**Requirement:** Create a formatter module that takes raw weather API response and formats it into a readable dashboard display format.

**Acceptance Criteria:**
- Formatter function returns formatted string containing temperature, humidity, wind speed, and weather description

**QA Status:** PASS
**Tech Stack:** python-dotenv, requests, pytest

---

### Story 3: CLI Interface Implementation — ✅ DONE

**Requirement:** Create main module that accepts city name as command line argument, calls weather service, formats output, and displays the weather dashboard.

**Acceptance Criteria:**
- Running py -m src.main "Dallas" displays formatted weather dashboard with current conditions

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
