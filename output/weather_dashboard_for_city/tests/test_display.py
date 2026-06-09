import pytest
from src.display import display_weather

SAMPLE = {
    "city": "London",
    "temperature": 18.5,
    "humidity": 72,
    "wind_speed": 5.2,
    "description": "light rain",
}

def test_display_weather_prints_all_fields(capsys):
    display_weather(SAMPLE)
    captured = capsys.readouterr().out
    assert "London" in captured
    assert "18.5" in captured
    assert "72" in captured
    assert "5.2" in captured
    assert "light rain" in captured

def test_display_weather_prints_units(capsys):
    display_weather(SAMPLE)
    captured = capsys.readouterr().out
    assert "°C" in captured
    assert "%" in captured
    assert "m/s" in captured

def test_display_weather_returns_none():
    result = display_weather(SAMPLE)
    assert result is None