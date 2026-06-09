from unittest.mock import patch, MagicMock
from src.weather import get_weather


def test_get_weather_happy_path():
    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.ok = True
    fake_response.json.return_value = {
        "name": "Dallas",
        "main": {"temp": 85.3, "humidity": 60},
        "wind": {"speed": 10.5},
        "weather": [{"description": "clear sky"}],
    }

    with patch("src.weather.requests.get", return_value=fake_response):
        result = get_weather("Dallas")

    assert result == {
        "city": "Dallas",
        "temperature": 85.3,
        "humidity": 60,
        "wind_speed": 10.5,
        "description": "clear sky",
    }