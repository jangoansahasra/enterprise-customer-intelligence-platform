# Testing

## Overview

This project includes automated tests for core transformation logic and API request validation.

The goal of the test suite is to verify important behavior without requiring the full raw dataset, PostgreSQL database, Docker container, or trained ML model artifacts to be available during every test run.

## Test Folder

Tests are stored in:

```text
tests/
```

Current test files:

```text
tests/test_transform_taxi_data.py
tests/test_api.py
```

## Run Tests

Run the full test suite:

```bash
python -m pytest
```

Run transformation tests only:

```bash
python -m pytest tests/test_transform_taxi_data.py
```

Run API tests only:

```bash
python -m pytest tests/test_api.py
```

## Current Coverage

### Transformation Tests

The transformation tests validate:

- raw TLC column standardization
- invalid trip filtering
- trip duration calculation
- pickup hour extraction
- pickup month extraction
- pickup day-of-week extraction
- weekend flag derivation
- fare per mile calculation
- tip percentage calculation
- pickup and dropoff zone enrichment

These tests focus on the logic in:

```text
etl/transform/transform_taxi_data.py
```

### API Tests

The API tests validate:

- root endpoint response
- OpenAPI route registration
- analytics route registration
- prediction route registration
- analytical prediction request schema validation
- pre-trip prediction request schema validation
- rejection of invalid prediction inputs

These tests focus on the logic in:

```text
api/main.py
api/routes/predictions.py
```

## Why Tests Avoid the Live Database

Some API endpoints require a running PostgreSQL database. The lightweight unit tests avoid live database dependency so they can run quickly in any local environment.

Database-connected behavior is still verified manually with commands such as:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/analytics/trips/summary
```

This keeps automated tests fast while still allowing full integration testing when Docker/PostgreSQL is running.

## Expected Result

A successful test run should show all tests passing.

Example:

```text
11 passed
```

## Future Testing Improvements

Potential future test additions:

- validation rule tests
- loader function tests with a temporary database
- API integration tests with Docker Compose
- SQL view smoke tests
- ML prediction tests using small sample model fixtures
- pipeline orchestration tests