import pytest
from unittest.mock import patch, MagicMock
from src.main import parse_arguments, main
from src.weather import format_weather_dashboard

def test_parse_arguments():
    with patch('sys.argv', ['main.py', 'Dallas']):
        args = parse_arguments()
        assert args.city == 'Dallas'

def test_format_weather_dashboard():
    weather_data = {
        'name': 'Dallas',
        'sys': {'country': 'US'},
        'main': {'temp': 25.0, 'humidity': 60},
        'weather': [{'description': 'clear sky'}],
        'wind': {'speed': 5.5}
    }
    
    dashboard = format_weather_dashboard(weather_data)
    assert 'Dallas, US' in dashboard
    assert '25.0°C' in dashboard
    assert '77.0°F' in dashboard
    assert 'Clear Sky' in dashboard
    assert '60%' in dashboard
    assert '5.5 m/s' in dashboard

@patch('src.main.fetch_weather_data')
@patch('sys.argv', ['main.py', 'TestCity'])
def test_main_success(mock_fetch):
    mock_fetch.return_value = {
        'name': 'TestCity',
        'sys': {'country': 'TC'},
        'main': {'temp': 20.0, 'humidity': 50},
        'weather': [{'description': 'sunny'}],
        'wind': {'speed': 3.0}
    }
    main()