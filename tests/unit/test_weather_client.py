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

    # Act & Assert
    result = get_hourly_forecast(48.13,11.57)

    # Assert that the result is an instance of WeatherData and has the expected values
    assert isinstance(result, WeatherData)
    assert result.outside_temperature == 19.5
    assert result.timestamp == "2026-08-12T18:00"

    # Assert that the request was made with the correct parameters
    assert len(responses.calls) == 1
    request = responses.calls[0].request
    assert "latitude=48.13" in request.url
    assert "longitude=11.57" in request.url
    assert "temperature_2m" in request.url

@responses.activate
def test_get_hourly_forecast_raises_timeout_error_for_timeout_response():
    # Arrange
    responses.add(
        responses.GET,
        url,
        body=requests.exceptions.Timeout("Server took too long to respond"),
    )
    
    # Act & Assert
    with pytest.raises(WeatherClientError) as captured:
         get_hourly_forecast(48.13, 11.57)

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

@responses.activate
def test_get_hourly_forecast_translates_http_200_with_malformed_weather_data():
    # Arrange
    responses.add(
        responses.GET,
        url,
        body="{malformed json",
        status=200,
        content_type="application/json"
    )

    # Act & Assert
    with pytest.raises(WeatherClientError) as captured:
        get_hourly_forecast(48.13, 11.57)

    assert captured.value.code == "INVALID_JSON"
    assert captured.value.retryable is False

@responses.activate
def test_get_hourly_forecast_translates_http_200_with_missing_temperature_data():
    # Arrange
    responses.add(
        responses.GET,
        url,
        json={"hourly": {"time": ["2026-08-12T18:00"]}},
        status=200,
    )

    # Act & Assert
    with pytest.raises(WeatherClientError) as captured:
        get_hourly_forecast(48.13, 11.57)

    assert captured.value.code == "INVALID_PAYLOAD"
    assert captured.value.retryable is False

@responses.activate
def test_get_hourly_forecast_translates_http_200_with_missing_time_data():
    # Arrange
    responses.add(
        responses.GET,
        url,
        json={"hourly": {"temperature_2m": [20.0]}},
        status=200,
    )

    # Act & Assert
    with pytest.raises(WeatherClientError) as captured:
        get_hourly_forecast(48.13, 11.57)

    assert captured.value.code == "INVALID_PAYLOAD"
    assert captured.value.retryable is False

@responses.activate
def test_get_hourly_forecast_translates_http_200_with_empty_arrays():
    # Arrange
    responses.add(
        responses.GET,
        url,
        json={"hourly": {"time": [], "temperature_2m": []}},
        status=200,
    )

    # Act & Assert
    with pytest.raises(WeatherClientError) as captured:
        get_hourly_forecast(48.13, 11.57)

    assert captured.value.code == "INVALID_PAYLOAD"
    assert captured.value.retryable is False

@responses.activate
def test_get_hourly_forecast_translates_http_200_with_temperature_returning_warm():
    # Arrange
    responses.add(
        responses.GET,
        url,
        json={"hourly": {"time": ["2026-08-12T18:00"], "temperature_2m": ["warm"]}},
        status=200,
    )

    # Act & Assert
    with pytest.raises(WeatherClientError) as captured:
        get_hourly_forecast(48.13, 11.57)

    assert captured.value.code == "INVALID_PAYLOAD"
    assert captured.value.retryable is False

@responses.activate
def test_get_hourly_forecast_translates_http_200_with_timestamp_returning_numeric_value():
    # Arrange
    responses.add(
        responses.GET,
        url,
        json={"hourly": {"time": [1234567890], "temperature_2m": [20.0]}},
        status=200,
    )

    # Act
    with pytest.raises(WeatherClientError) as captured:
        get_hourly_forecast(48.13, 11.57)

    # Assert
    assert captured.value.code == "INVALID_PAYLOAD"
    assert captured.value.retryable is False

@responses.activate
@pytest.mark.parametrize(
    "temperature",
    [0, -5.5, 19.75],
)
def test_get_hourly_forecast_accepts_valid_numeric_temperatures(temperature):
    # Arrange
    payload = {
        "hourly": {
            "time": ["2026-08-12T18:00"],
            "temperature_2m": [temperature],
        }
    }

    responses.add(
        responses.GET,
        url,
        json=payload,
        status=200,
    )

    # Act
    result = get_hourly_forecast(48.13,11.57)

    # Assert
    assert isinstance(result, WeatherData)
    assert result.outside_temperature == temperature

@responses.activate
@pytest.mark.parametrize(
    "temperature",
    [None, True, "19.5", {}, []],
)
def test_get_hourly_forecast_rejects_invalid_temperature_values(temperature):
    # Arrange
    responses.add(
        responses.GET,
        url,
        json={"hourly": {"time": ["2026-08-12T18:00"], "temperature_2m": [temperature]}},
        status=200,
    )
    
    # Act & Assert
    with pytest.raises(WeatherClientError) as captured:
        get_hourly_forecast(48.13, 11.57)

    assert captured.value.code == "INVALID_PAYLOAD"
    assert captured.value.retryable is False
