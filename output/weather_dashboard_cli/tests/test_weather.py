from unittest.mock import patch, MagicMock
from src.weather import get_weather

FAKE_RESPONSE = {
    "main": {"temp": 72.5, "humidity": 60},
    "wind": {"speed": 10.3},
    "weather": [{"description": "clear sky"}],
}


def test_get_weather_returns_expected_keys():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = FAKE_RESPONSE

    with patch("src.weather.requests.get", return_value=mock_resp):
        result = get_weather("Dallas")

    assert result == {
        "city": "Dallas",
        "temperature": 72.5,
        "humidity": 60,
        "wind_speed": 10.3,
        "description": "clear sky",
    }