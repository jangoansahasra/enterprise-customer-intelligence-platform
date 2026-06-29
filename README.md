# Enterprise Urban Mobility Data Platform

An end-to-end data engineering and analytics platform built with NYC Yellow Taxi trip data.

This project simulates a transportation agency data platform that ingests raw taxi trip records, validates and transforms over 10 million records, loads analytics-ready data into PostgreSQL, exposes insights through FastAPI, and trains machine learning models for trip duration prediction.

## Business Problem

City transportation agencies receive millions of taxi trip records every month, but raw operational data is not immediately useful for analytics or decision-making.

Analysts and mobility planners need trusted, queryable data to answer questions such as:

- which pickup and dropoff zones have the highest demand
- which boroughs generate the most revenue
- how demand changes by hour, weekday, and month
- which zone and borough patterns drive trip activity
- whether machine learning can estimate trip duration from trip features

This project solves that problem by converting raw NYC taxi records into validated, cleaned, analytics-ready, API-accessible, and ML-ready datasets.

## Platform Capabilities

- raw data profiling and validation
- large-scale taxi trip transformation with Python and Pandas
- PostgreSQL fact and dimension data model
- SQL analytics views for reporting and BI use cases
- FastAPI analytics endpoints
- machine learning models for trip duration prediction
- automated unit tests for transformation and API logic
- dashboard planning for Power BI

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

Files used:

```text
data/raw/
├── yellow_tripdata_2025-01.parquet
├── yellow_tripdata_2025-02.parquet
├── yellow_tripdata_2025-03.parquet
└── taxi_zone_lookup.csv
```

The taxi zone lookup file maps TLC location IDs to boroughs, zones, and service zones.

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
PostgreSQL Database
        ↓
SQL Analytics Views
        ↓
FastAPI Analytics + Prediction API
        ↓
Machine Learning Models
        ↓
Power BI Dashboard Preparation
```

## Project Structure

```text
enterprise-urban-mobility-data-platform/
├── api/
├── database/
├── data/
├── docs/
├── etl/
├── ml/
├── sql/
├── tests/
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Key Results

Final transformed dataset:

```text
10,413,054 cleaned taxi trip records
34 analytics-ready columns
```

PostgreSQL full load:

```text
fact_trips: 10,413,054 rows
dim_location: 265 rows
dim_vendor: 4 rows
dim_payment_type: 7 rows
```

Data quality checks after full load:

```text
required null fields: 0
invalid business rule violations: 0
missing foreign key matches: 0
duplicate-like records: 0
```

## Quick Start

Install dependencies:

```bash
pip install -r requirements.txt
```

Start PostgreSQL:

```bash
docker compose up -d
```

Create database schema:

```bash
docker exec -i urban_mobility_postgres psql -U urban_user -d urban_mobility_db < database/schema.sql
docker exec -i urban_mobility_postgres psql -U urban_user -d urban_mobility_db < database/seed_reference_tables.sql
docker exec -i urban_mobility_postgres psql -U urban_user -d urban_mobility_db < database/indexes.sql
```

Run the ETL pipeline:

```bash
python -m etl.pipeline
```

Load the full cleaned dataset into PostgreSQL:

```bash
LOAD_SAMPLE_SIZE=0 python etl/load/load_to_postgres.py
```

Create analytics views:

```bash
docker exec -i urban_mobility_postgres psql -U urban_user -d urban_mobility_db < sql/analytics_views.sql
```

Run the API:

```bash
python -m uvicorn api.main:app --reload
```

Open API documentation:

```text
http://127.0.0.1:8000/docs
```

## SQL Analytics Views

The project creates reusable analytics views:

```text
vw_daily_trip_summary
vw_hourly_demand
vw_borough_revenue
vw_zone_performance
vw_payment_summary
vw_ml_trip_features
```

These views support reporting, API endpoints, BI dashboards, and ML feature generation.

## API Endpoints

Main endpoints:

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

Example summary response:

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

| Model | Purpose | MAE | RMSE | R2 |
|---|---|---:|---:|---:|
| Analytical model | Uses trip, location, payment, fare, and total amount fields | 1.35 min | 3.40 min | 0.9129 |
| Pre-trip model | Excludes post-trip fare, total, and tip fields | 3.18 min | 5.13 min | 0.8094 |

The analytical model performs better because fare and total amount are strongly related to trip duration, but the pre-trip model is more realistic for prediction before a trip is completed.

## Testing

Run all tests:

```bash
python -m pytest
```

Current test coverage includes:

- transformation logic
- invalid trip filtering
- derived time and financial features
- taxi zone enrichment
- FastAPI route registration
- prediction request schema validation

Current suite:

```text
11 passing tests
```

## Documentation

Detailed documentation is available in:

```text
docs/project_overview.md
docs/data_dictionary.md
docs/database_design.md
docs/etl_design.md
docs/api_documentation.md
docs/ml_modeling.md
docs/dashboard_summary.md
docs/testing.md
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

## Summary

Enterprise Urban Mobility Data Platform | Python, PostgreSQL, FastAPI, Docker, Power BI

Built an end-to-end data engineering platform that ingested 3 months of NYC yellow taxi trip records, validated and transformed over 10 million records, loaded analytics-ready datasets into PostgreSQL, created SQL analytics views, exposed metrics through FastAPI endpoints, and trained machine learning models for trip duration prediction.