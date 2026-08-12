import pytest
import requests
import responses


from smart_home_qa_harness.weather_client import (
    WeatherClientError,
    WeatherData,
    get_hourly_forecast,
)

url = "https://api.open-meteo.com/v1/forecast"

@responses.activate
def test_get_hourly_forecast_returns_weather_data_for_valid_response():
    # Arrange
    payload = {
        "hourly": {
            "time": ["2026-08-12T18:00"],
            "temperature_2m": [19.5],
        }
    }

    responses.add(
        responses.GET,
        url,
        json=payload,
        status=200,
    )

    # Act
    result = get_hourly_forecast(
        lat=48.1374,
        long=11.5755,
    )

    # Assert
    # Assert that the result is an instance of WeatherData and has the expected values
    assert isinstance(result, WeatherData)
    assert result.outside_temperature == 19.5
    assert result.timestamp == "2026-08-12T18:00"

    # Assert that the request was made with the correct parameters
    assert len(responses.calls) == 1
    request = responses.calls[0].request
    assert "latitude=48.1374" in request.url
    assert "longitude=11.5755" in request.url
    assert "temperature_2m" in request.url

@responses.activate
def test_get_hourly_forecast_raises_timeout_error_for_timeout_response():
    # Arrange
    responses.add(
        responses.GET,
        url,
        body=requests.exceptions.Timeout("Server took too long to respond"),
    )
    
    # Act
    with pytest.raises(WeatherClientError) as captured:
         get_hourly_forecast(48.13, 11.57)

    # Assert
    error = captured.value
    assert error.code == "TIMEOUT"
    assert error.retryable is True

@responses.activate
def test_get_hourly_forecast_translates_http_500_to_weather_client_error():
    # Arrange
    responses.add(
        responses.GET,
        url,
        json={"error": "Internal Server Error"},
        status=500,
    )

    # Act & Assert
    with pytest.raises(WeatherClientError) as captured:
        get_hourly_forecast(48.13, 11.57)

    assert captured.value.code == "HTTP_ERROR"
    assert captured.value.retryable is True
    assert "500" in captured.value.message

