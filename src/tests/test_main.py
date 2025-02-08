import pytest
import requests
import time
from app.utils import base62_encode
# Base URL of the FastAPI app
BASE_URL = "http://localhost:8000"


# Fixture to start the FastAPI app
@pytest.fixture(scope="module")
# Tests
def test_shorten_url():
    response = requests.post(f"{BASE_URL}/shorten/", json={"long_url": "https://example.com"})
    assert response.status_code == 200
    assert "short_url" in response.json()

def test_redirect_url():
    response = requests.post(f"{BASE_URL}/shorten/", json={"long_url": "https://example.com"})
    short_url = response.json()["short_url"]
    short_code = short_url.split("/")[-1]

    response = requests.get(f"{BASE_URL}/{short_code}", allow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "https://example.com/"

    response = requests.get(f"{BASE_URL}/invalid", allow_redirects=False)
    assert response.status_code == 404

@pytest.mark.parametrize(
    "number, expected",
    [
        (0, "0"),          # Test zero
        (1, "1"),          # Single character (digit)
        (10, "A"),         # Single character (uppercase)
        (35, "Z"),         # Uppercase boundary
        (36, "a"),         # Lowercase start
        (61, "z"),         # Lowercase boundary
        (62, "10"),        # Two characters
        (12345, "3D7"),    # Multi-character mix
        (238327, "zzz"),   # Large number with all 'z's
        (3844, "100"),     # Exact multiple of base (62^2)
        (-1, ""),          # Negative number (invalid input)
        (-100, ""),        # Negative number (invalid input)
        (238328, "1000"),  # Large number (62^3)
    ],
)
def test_base62_encode(number, expected):
    assert base62_encode(number) == expected
