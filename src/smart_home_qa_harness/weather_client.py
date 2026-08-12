import requests
from dataclasses import dataclass

# --- Coordinates ---
lat = 48.1374  # Munich
long = 11.5755

@dataclass(frozen=True)
class WeatherData:
    outside_temperature: float
    timestamp: str

class WeatherClientError(Exception):
    def __init__(self, code: str, message: str, retryable: bool):
        super().__init__(message)
        self.message = message
        self.code = code
        self.retryable = retryable


def get_hourly_forecast(lat, long):
    """
    Get hourly forecast for the given coordinates.
    :param lat: Latitude
    :param long: Longitude
    :return: JSON response from the weather API
    """
    url = "https://api.open-meteo.com/v1/forecast"
    timeout = 3 # Seconds
    params = {
        "latitude": lat,
        "longitude": long,
        "hourly": "temperature_2m"
    }

    try:
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        payload=response.json()

    except requests.exceptions.HTTPError as e:
        # A response arrived, but its status was 4xx/5xx
        raise WeatherClientError("HTTP_ERROR", f"Failed to fetch weather data: {response.status_code} - {response.text}", True) from e
    except requests.exceptions.Timeout as e:
        # No usable HTTP response arrived
        raise WeatherClientError("TIMEOUT", "Request to weather API timed out", True) from e

    return WeatherData(
        outside_temperature=payload["hourly"]["temperature_2m"][0],
        timestamp=payload["hourly"]["time"][0],
        )

