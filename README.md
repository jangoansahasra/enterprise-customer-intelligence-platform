# Enterprise Urban Mobility Data Platform

An end-to-end data engineering and analytics platform built with NYC Yellow Taxi trip data.

This project simulates a real urban mobility data platform for a transportation agency. It ingests raw taxi trip records, profiles and validates data quality, transforms records into analytics-ready datasets, loads cleaned data into PostgreSQL, creates SQL analytics views, exposes insights through FastAPI endpoints, and trains machine learning models for trip duration prediction.

## Business Problem

City transportation agencies receive millions of taxi trip records every month, but raw operational data is not immediately useful for analytics or decision-making.

Analysts and mobility planners need trusted, queryable data to answer questions such as:

- which pickup and dropoff zones have the highest demand
- which boroughs generate the most revenue
- how demand changes by hour, weekday, and month
- which zones and borough pairs drive the most trip activity
- how payment type, distance, fare, and location relate to trip behavior
- whether machine learning can estimate trip duration from trip features

This project addresses that problem by building a data platform that converts raw NYC taxi records into validated, cleaned, analytics-ready, API-accessible, and ML-ready datasets.

## Project Goals

The goal of this project is to build a realistic urban mobility data platform that supports:

- raw data ingestion from NYC TLC trip records
- automated data profiling and validation
- cleaning and transformation of large-scale taxi trip data
- PostgreSQL data warehouse modeling with fact and dimension tables
- SQL analytics views for reporting and BI use cases
- FastAPI endpoints for analytics and prediction access
- machine learning workflows for trip duration prediction
- Power BI dashboard preparation

## Skills Demonstrated

This project demonstrates practical skills in:

- data engineering
- analytics engineering
- backend API development
- SQL analytics
- data quality validation
- machine learning workflow development
- BI/dashboard preparation

## Tech Stack

- Python
- Pandas
- NumPy
- PostgreSQL
- SQLAlchemy
- FastAPI
- Uvicorn
- Docker
- Scikit-learn
- XGBoost
- Pytest
- Power BI

## Dataset

Source: NYC Taxi & Limousine Commission Trip Record Data

Data used:

```text
data/raw/
├── yellow_tripdata_2025-01.parquet
├── yellow_tripdata_2025-02.parquet
├── yellow_tripdata_2025-03.parquet
└── taxi_zone_lookup.csv
```

The taxi zone lookup file maps location IDs to boroughs, zones, and service zones.

## Architecture

```text
Raw NYC Taxi Data
        ↓
Data Profiling
        ↓
Data Validation
        ↓
Python ETL Transformation
        ↓
Processed Parquet Dataset
        ↓
PostgreSQL Data Warehouse
        ↓
SQL Analytics Views
        ↓
FastAPI Analytics + Prediction API
        ↓
Machine Learning Models
        ↓
Power BI Dashboard
```

## Project Structure

```text
enterprise-urban-mobility-data-platform/
├── api/
│   ├── main.py
│   ├── database.py
│   └── routes/
│       ├── analytics.py
│       └── predictions.py
├── database/
│   ├── schema.sql
│   ├── indexes.sql
│   └── seed_reference_tables.sql
├── data/
│   ├── raw/
│   ├── processed/
│   └── validation_reports/
├── docs/
│   ├── api_documentation.md
│   └── ml_modeling.md
├── etl/
│   ├── profile/
│   ├── validate/
│   ├── transform/
│   ├── load/
│   └── pipeline.py
├── ml/
│   ├── train_model.py
│   ├── train_pretrip_model.py
│   ├── predict.py
│   └── models/
├── sql/
│   ├── analytics_views.sql
│   ├── data_quality_checks.sql
│   └── sample_queries.sql
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Data Profiling

The profiling module inspects raw input files and reports:

- row counts
- column counts
- data types
- missing values
- duplicate rows
- numeric statistics
- memory usage
- date ranges
- suspicious values

Run:

```bash
python etl/profile/profile_raw_data.py
```

Output:

```text
data/validation_reports/raw_data_profile.csv
```

## Data Validation

The validation module checks for:

- missing pickup/dropoff timestamps
- dropoff time before pickup time
- non-positive trip distance
- non-positive fare amount
- negative total amount
- invalid payment types
- missing location IDs
- location IDs missing from taxi zone lookup
- duplicate-like records
- extreme duration, distance, and fare outliers

Run:

```bash
python etl/validate/validate_taxi_data.py
```

Outputs:

```text
data/validation_reports/taxi_data_validation_summary.csv
data/validation_reports/taxi_data_invalid_records_sample.csv
```

## ETL Pipeline

The ETL pipeline profiles, validates, transforms, and optionally loads the data.

Run profiling, validation, and transformation:

```bash
python -m etl.pipeline
```

Run pipeline with PostgreSQL load:

```bash
python -m etl.pipeline --load
```

The transformation step creates:

```text
data/processed/cleaned_taxi_trips_2025_q1.parquet
```

Final cleaned dataset:

```text
10,413,054 rows
34 columns
```

## PostgreSQL Database

The database contains dimension and fact tables:

```text
dim_vendor
dim_payment_type
dim_location
fact_trips
```

Start PostgreSQL with Docker Compose:

```bash
docker compose up -d
```

Create schema:

```bash
docker exec -i urban_mobility_postgres psql -U urban_user -d urban_mobility_db < database/schema.sql
docker exec -i urban_mobility_postgres psql -U urban_user -d urban_mobility_db < database/seed_reference_tables.sql
docker exec -i urban_mobility_postgres psql -U urban_user -d urban_mobility_db < database/indexes.sql
```

Load cleaned data:

```bash
LOAD_SAMPLE_SIZE=0 python etl/load/load_to_postgres.py
```

Full loaded row count:

```text
fact_trips: 10,413,054 rows
```

## SQL Analytics Views

The project creates analytics-ready SQL views:

```text
vw_daily_trip_summary
vw_hourly_demand
vw_borough_revenue
vw_zone_performance
vw_payment_summary
vw_ml_trip_features
```

Create views:

```bash
docker exec -i urban_mobility_postgres psql -U urban_user -d urban_mobility_db < sql/analytics_views.sql
```

Run data quality checks:

```bash
docker exec -i urban_mobility_postgres psql -U urban_user -d urban_mobility_db < sql/data_quality_checks.sql
```

## FastAPI Layer

Run the API:

```bash
python -m uvicorn api.main:app --reload
```

Open Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Main API endpoints:

```text
GET  /health
GET  /analytics/trips/summary
GET  /analytics/revenue/by-borough
GET  /analytics/demand/by-hour
GET  /analytics/zones/top-pickups
GET  /analytics/payments/summary
POST /predict/trip-duration
POST /predict/pretrip-duration
```

Example trip summary response:

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

## Machine Learning

The project includes two trip duration prediction models.

### Analytical Model

The analytical model uses trip, location, payment, and fare-related features.

Features include:

```text
pickup_hour
pickup_day_of_week
pickup_month
is_weekend
passenger_count
trip_distance
fare_amount
total_amount
pickup_borough
dropoff_borough
payment_type_id
```

Metrics:

```text
MAE:  1.35 minutes
RMSE: 3.40 minutes
R2:   0.9129
```

This model performs strongly, but includes post-trip fields such as fare and total amount.

### Pre-Trip Model

The pre-trip model excludes post-trip financial fields.

Excluded fields:

```text
fare_amount
total_amount
tip_amount
```

Metrics:

```text
MAE:  3.18 minutes
RMSE: 5.13 minutes
R2:   0.8094
```

This model is more realistic for predicting trip duration before or at pickup time.

Train models:

```bash
python ml/train_model.py
python ml/train_pretrip_model.py
```

## Prediction API Example

Pre-trip prediction request:

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

## Data Quality Results

After cleaning and loading the full dataset:

```text
fact_trips: 10,413,054 rows
required null fields: 0
invalid business rule violations: 0
missing foreign key matches: 0
duplicate-like records: 0
```

Remaining known data quality notes:

- some trips have missing passenger count
- some valid but extreme trips remain as outliers
- TLC monthly files include a small number of boundary records near month edges

These are documented and handled through validation and transformation logic.

## Documentation

Additional project documentation:

```text
docs/api_documentation.md
docs/ml_modeling.md
```
## Testing

The project includes automated tests for core transformation logic and API request validation.

Run all tests:

```bash
python -m pytest
```

## Future Improvements

Planned enhancements:

- Power BI dashboard
- Airflow orchestration
- dbt transformation layer
- weather and holiday enrichment
- model comparison with Linear Regression, Random Forest, and XGBoost
- model monitoring and drift tracking
- deployment-ready API containerization

## Resume Summary

Enterprise Urban Mobility Data Platform | Python, PostgreSQL, FastAPI, Docker, Power BI

Built an end-to-end data engineering platform that ingested 3 months of NYC yellow taxi trip records, validated and transformed over 10 million records, loaded analytics-ready datasets into PostgreSQL, created SQL analytics views, exposed metrics through FastAPI endpoints, and trained machine learning models for trip duration prediction.