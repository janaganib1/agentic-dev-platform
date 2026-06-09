import subprocess
import sys
from unittest.mock import patch, MagicMock

PYTHON = sys.executable


def test_valid_city():
    mock_data = {
        "name": "Dallas", "sys": {"country": "US"},
        "main": {"temp": 75, "feels_like": 73, "humidity": 50},
        "weather": [{"description": "clear sky"}], "wind": {"speed": 5}
    }
    with patch("src.story1.requests.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=200, json=lambda: mock_data)
        result = subprocess.run(
            [PYTHON, "-m", "src.main", "Dallas"],
            capture_output=True, text=True
        )
    assert result.returncode == 0
    assert "Dallas" in result.stdout


def test_no_argument():
    result = subprocess.run(
        [PYTHON, "-m", "src.main"],
        capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "Usage" in result.stdout


def test_invalid_city():
    with patch("src.story1.requests.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=404)
        result = subprocess.run(
            [PYTHON, "-m", "src.main", "FakeCity123"],
            capture_output=True, text=True
        )
    assert result.returncode == 1
    assert "FakeCity123" in result.stdout