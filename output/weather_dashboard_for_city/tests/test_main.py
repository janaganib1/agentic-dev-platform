import pytest
from unittest.mock import patch


FAKE_DATA = {"city": "Dallas", "country": "US", "temp": 72, "feels_like": 70,
             "humidity": 45, "description": "Sunny", "wind_speed": 5}


def test_valid_city_displays_weather():
    with patch("src.weather.fetch_weather", return_value=FAKE_DATA) as mock_fetch, \
         patch("src.weather.display_weather") as mock_display, \
         patch("sys.argv", ["main", "Dallas"]):
        from src.main import main
        main()
    mock_fetch.assert_called_once_with("Dallas")
    mock_display.assert_called_once_with(FAKE_DATA)


def test_invalid_city_exits_with_code_1():
    with patch("src.weather.fetch_weather", return_value=None), \
         patch("sys.argv", ["main", "InvalidCity999"]):
        from src.main import main
        with pytest.raises(SystemExit) as exc:
            main()
    assert exc.value.code == 1