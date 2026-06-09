from src.display import display_weather

def test_display_weather_prints_all_fields(capsys):
    data = {
        "city": "London",
        "temperature": 22,
        "humidity": 60,
        "wind_speed": 14,
        "description": "Clear sky",
    }
    display_weather(data)
    captured = capsys.readouterr()

    assert "London" in captured.out
    assert "22°C" in captured.out
    assert "60%" in captured.out
    assert "14 km/h" in captured.out
    assert "Clear sky" in captured.out