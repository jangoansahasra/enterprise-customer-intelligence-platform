from fastapi.testclient import TestClient
from pydantic import ValidationError
import pytest

from api.main import app
from api.routes.predictions import (
    PreTripDurationPredictionRequest,
    TripDurationPredictionRequest,
)


client = TestClient(app)


def test_root_endpoint() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Enterprise Urban Mobility Data Platform API",
        "docs": "/docs",
    }


def test_openapi_schema_includes_expected_routes() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200

    paths = response.json()["paths"]

    assert "/" in paths
    assert "/health" in paths
    assert "/analytics/trips/summary" in paths
    assert "/analytics/revenue/by-borough" in paths
    assert "/analytics/demand/by-hour" in paths
    assert "/analytics/zones/top-pickups" in paths
    assert "/analytics/payments/summary" in paths
    assert "/predict/trip-duration" in paths
    assert "/predict/pretrip-duration" in paths


def test_trip_duration_prediction_request_accepts_valid_payload() -> None:
    request = TripDurationPredictionRequest(
        pickup_hour=14,
        pickup_day_of_week="Wednesday",
        pickup_month=1,
        is_weekend=False,
        passenger_count=1,
        trip_distance=3.2,
        fare_amount=18.5,
        total_amount=24.3,
        pickup_borough="Manhattan",
        dropoff_borough="Manhattan",
        payment_type_id=1,
    )

    assert request.pickup_hour == 14
    assert request.trip_distance == 3.2
    assert request.fare_amount == 18.5


def test_trip_duration_prediction_request_rejects_invalid_hour() -> None:
    with pytest.raises(ValidationError):
        TripDurationPredictionRequest(
            pickup_hour=24,
            pickup_day_of_week="Wednesday",
            pickup_month=1,
            is_weekend=False,
            passenger_count=1,
            trip_distance=3.2,
            fare_amount=18.5,
            total_amount=24.3,
            pickup_borough="Manhattan",
            dropoff_borough="Manhattan",
            payment_type_id=1,
        )


def test_pretrip_prediction_request_does_not_require_fare_fields() -> None:
    request = PreTripDurationPredictionRequest(
        pickup_hour=14,
        pickup_day_of_week="Wednesday",
        pickup_month=1,
        is_weekend=False,
        passenger_count=1,
        trip_distance=3.2,
        pickup_borough="Manhattan",
        dropoff_borough="Manhattan",
        payment_type_id=1,
    )

    assert request.pickup_hour == 14
    assert request.trip_distance == 3.2
    assert not hasattr(request, "fare_amount")
    assert not hasattr(request, "total_amount")


def test_pretrip_prediction_request_rejects_non_positive_distance() -> None:
    with pytest.raises(ValidationError):
        PreTripDurationPredictionRequest(
            pickup_hour=14,
            pickup_day_of_week="Wednesday",
            pickup_month=1,
            is_weekend=False,
            passenger_count=1,
            trip_distance=0,
            pickup_borough="Manhattan",
            dropoff_borough="Manhattan",
            payment_type_id=1,
        )