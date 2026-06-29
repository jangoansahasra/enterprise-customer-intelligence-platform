# API Documentation

## Overview

The FastAPI layer exposes analytics and machine learning predictions from the PostgreSQL urban mobility database.

The API reads from SQL analytics views and fact/dimension tables created from cleaned NYC Yellow Taxi trip data.

## Run Locally

Start PostgreSQL with Docker Compose:

```bash
docker compose up -d
```

Run the FastAPI server:

```bash
python -m uvicorn api.main:app --reload
```

Open the interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## Health Check

```text
GET /health
```

Checks whether the API is running and whether the database connection works.

Example:

```bash
curl http://127.0.0.1:8000/health
```

Example response:

```json
{
  "status": "healthy",
  "database": "connected"
}
```

## Analytics Endpoints

### Trip Summary

```text
GET /analytics/trips/summary
```

Returns platform-level trip, revenue, fare, distance, duration, and tip summary metrics.

Example:

```bash
curl http://127.0.0.1:8000/analytics/trips/summary
```

Example response:

```json
{
  "total_trips": 10413054,
  "total_revenue": "283836767.29",
  "avg_fare_amount": "18.52",
  "avg_trip_distance": "5.83",
  "avg_trip_duration_minutes": "15.60",
  "avg_tip_percentage": "19.08"
}
```

### Revenue By Borough

```text
GET /analytics/revenue/by-borough
```

Returns revenue and trip metrics by pickup and dropoff borough.

Example:

```bash
curl "http://127.0.0.1:8000/analytics/revenue/by-borough?limit=10"
```

### Demand By Hour

```text
GET /analytics/demand/by-hour
```

Returns hourly trip demand and revenue patterns.

Example:

```bash
curl http://127.0.0.1:8000/analytics/demand/by-hour
```

### Top Pickup Zones

```text
GET /analytics/zones/top-pickups
```

Returns the highest-demand pickup zones.

Example:

```bash
curl "http://127.0.0.1:8000/analytics/zones/top-pickups?limit=5"
```

Example response:

```json
[
  {
    "pickup_borough": "Manhattan",
    "pickup_zone": "Midtown Center",
    "pickup_trips": 487188,
    "total_revenue": "12084375.55",
    "avg_total_amount": "24.80",
    "avg_trip_distance": "2.63",
    "avg_trip_duration_minutes": "14.47"
  }
]
```

### Payment Summary

```text
GET /analytics/payments/summary
```

Returns trip and revenue metrics by payment type.

Example:

```bash
curl http://127.0.0.1:8000/analytics/payments/summary
```

## Prediction Endpoints

### Analytical Trip Duration Prediction

```text
POST /predict/trip-duration
```

This endpoint predicts taxi trip duration using the analytical ML model.

This model includes post-trip financial fields such as:

```text
fare_amount
total_amount
```

Because fare and total amount are usually known after a trip is completed, this endpoint is useful for analytics, model experimentation, and understanding relationships in completed trip data.

Example request:

```bash
curl -X POST "http://127.0.0.1:8000/predict/trip-duration" \
  -H "Content-Type: application/json" \
  -d '{
    "pickup_hour": 14,
    "pickup_day_of_week": "Wednesday",
    "pickup_month": 1,
    "is_weekend": false,
    "passenger_count": 1,
    "trip_distance": 3.2,
    "fare_amount": 18.5,
    "total_amount": 24.3,
    "pickup_borough": "Manhattan",
    "dropoff_borough": "Manhattan",
    "payment_type_id": 1
  }'
```

Example response:

```json
{
  "predicted_trip_duration_minutes": 21.57
}
```

### Pre-Trip Duration Prediction

```text
POST /predict/pretrip-duration
```

This endpoint predicts taxi trip duration using only features that could reasonably be known before or at pickup time.

This model excludes post-trip financial fields such as:

```text
fare_amount
total_amount
tip_amount
```

This makes it more realistic for a production-style pre-trip prediction use case.

Example request:

```bash
curl -X POST "http://127.0.0.1:8000/predict/pretrip-duration" \
  -H "Content-Type: application/json" \
  -d '{
    "pickup_hour": 14,
    "pickup_day_of_week": "Wednesday",
    "pickup_month": 1,
    "is_weekend": false,
    "passenger_count": 1,
    "trip_distance": 3.2,
    "pickup_borough": "Manhattan",
    "dropoff_borough": "Manhattan",
    "payment_type_id": 1
  }'
```

Example response:

```json
{
  "predicted_trip_duration_minutes": 22.73
}
```

## Prediction Endpoint Comparison

| Endpoint | Purpose | Uses Fare/Total Amount? | Best Use Case |
|---|---|---:|---|
| `/predict/trip-duration` | Analytical trip duration prediction | Yes | Completed trip analysis and model experimentation |
| `/predict/pretrip-duration` | Pre-trip duration prediction | No | More realistic prediction before a trip is completed |

## Interactive Documentation

FastAPI automatically creates Swagger/OpenAPI documentation at:

```text
http://127.0.0.1:8000/docs
```

This page can be used to:

- view available endpoints
- inspect required request fields
- test API calls directly in the browser
- view response formats