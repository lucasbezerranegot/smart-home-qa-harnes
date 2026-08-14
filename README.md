# Smart Home QA Harness

A serverless-oriented Python application for testing and orchestrating smart-home environmental controls. The project emphasizes deterministic business logic, mocked external APIs, graceful failure handling, measurable quality gates, and reproducible Python 3.12 execution.

## Weather client

The weather client retrieves hourly temperature data from the Open-Meteo forecast API. It is intentionally separated from the decision engine so that HTTP behavior and business rules can be tested independently.

### Success contract

A successful request returns an immutable `WeatherData` value containing:

- `outside_temperature`: the first hourly temperature as an `int` or `float`.
- `timestamp`: the corresponding forecast timestamp as a non-empty string.

The current implementation selects the first hourly observation in the response. Selecting the observation that corresponds to the actual current hour is a possible future enhancement.

### Failure contract

Provider and transport failures are translated into `WeatherClientError`, which exposes:

- `code`: a stable application-level error code.
- `message`: a readable diagnostic message.
- `retryable`: whether retrying the operation may be appropriate.

| Failure | Error code | Retryable |
|---|---|---:|
| Request timeout | `TIMEOUT` | Yes |
| HTTP 4xx/5xx response | `HTTP_ERROR` | Yes |
| Malformed JSON | `INVALID_JSON` | No |
| Missing, empty, or incorrectly typed weather fields | `INVALID_PAYLOAD` | No |

The client always applies an HTTP timeout. Unit tests mock every Open-Meteo request with `responses` and cover successful responses, timeouts, HTTP 500 responses, malformed JSON, schema changes, and temperature type validation.

## Decision rules

The decision engine evaluates outside temperature, inside temperature, and a caller-supplied local time. Time boundaries are inclusive.

### Evening ventilation

Between 18:00 and 23:00:

- Return `OPEN_WINDOWS` when the outside temperature is lower than the inside temperature.
- Otherwise return `NO_ACTION`.

### Morning heat protection

Between 06:00 and 11:00:

- Return `CLOSE_WINDOWS` when the outside temperature is greater than or equal to the inside temperature.
- Also return `CLOSE_WINDOWS` when the outside temperature is at least 24°C, even if the apartment is currently warmer.
- Otherwise return `NO_ACTION`.

Outside these time windows, return `NO_ACTION`.

| Scenario | Time | Outside | Inside | Expected action |
|---|---:|---:|---:|---|
| Evening cooling | 20:00 | 18°C | 24°C | `OPEN_WINDOWS` |
| Equal evening temperatures | 20:00 | 24°C | 24°C | `NO_ACTION` |
| Outside warmer in morning | 10:00 | 23°C | 22°C | `CLOSE_WINDOWS` |
| Temperatures equal in morning | 10:00 | 23°C | 23°C | `CLOSE_WINDOWS` |
| Morning heat threshold | 10:00 | 24°C | 25°C | `CLOSE_WINDOWS` |
| Useful morning cooling | 10:00 | 23°C | 25°C | `NO_ACTION` |
| Before morning window | 05:59 | 24°C | 23°C | `NO_ACTION` |
| After morning window | 11:01 | 24°C | 23°C | `NO_ACTION` |
