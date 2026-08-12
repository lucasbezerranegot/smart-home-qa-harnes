import requests

# --- Coordinates ---
LAT = 48.1374  # Munich
LON = 11.5755


def get_hourly_forecast(lat, long):
    """
    Get hourly forecast for the given coordinates.
    :param lat: Latitude
    :param long: Longitude
    :return: JSON response from the weather API
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&hourly=temperature_2m"
    timeout = 3 # Seconds
    response = requests.get(url, timeout=timeout)
    if response.status_code == 200:
        return response.json()
    else:
        raise ValueError(f"Failed to fetch weather data: {response.status_code} - {response.text}")

