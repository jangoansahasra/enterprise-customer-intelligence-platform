# Project Completion Summary

## Project Name

Enterprise Urban Mobility Data Platform

## Summary

The Enterprise Urban Mobility Data Platform is an end-to-end data engineering, analytics, API, and machine learning project built with NYC Yellow Taxi trip data.

The platform ingests raw TLC taxi trip files, profiles and validates the data, transforms raw records into analytics-ready datasets, loads cleaned data into PostgreSQL, creates SQL analytics views, exposes metrics through FastAPI, and trains machine learning models for taxi trip duration prediction.

## Business Problem

City transportation agencies receive large volumes of trip records every month, but raw operational files are not immediately useful for decision-making.

This project solves that problem by turning raw taxi data into trusted datasets that can support:

- demand analysis
- revenue analysis
- borough and zone performance
- payment behavior analysis
- API-based analytics access
- machine learning trip duration prediction
- future Power BI dashboards

## Dataset

Source:

```text
NYC Taxi & Limousine Commission Trip Record Data
```

Raw files used:

```text
yellow_tripdata_2025-01.parquet
yellow_tripdata_2025-02.parquet
yellow_tripdata_2025-03.parquet
taxi_zone_lookup.csv
```

## Final Data Volume

Raw trip files processed:

```text
January 2025
February 2025
March 2025
```

Final cleaned dataset:

```text
10,413,054 rows
34 columns
```

PostgreSQL full load:

```text
fact_trips: 10,413,054 rows
dim_location: 265 rows
dim_vendor: 4 rows
dim_payment_type: 7 rows
```

## Completed Components

### Repository and Project Structure

Completed:

- organized project folder structure
- Git and GitHub setup
- requirements file
- Docker Compose setup
- `.gitignore`
- raw data storage
- processed data folder
- validation report folder
- documentation folder
- tests folder

### ETL Pipeline

Completed:

- raw data profiling
- taxi data validation
- taxi trip transformation
- processed Parquet output
- PostgreSQL loading
- modular ETL pipeline runner

Main scripts:

```text
etl/profile/profile_raw_data.py
etl/validate/validate_taxi_data.py
etl/transform/transform_taxi_data.py
etl/load/load_to_postgres.py
etl/pipeline.py
```

### Database Layer

Completed:

- PostgreSQL schema
- fact and dimension table design
- vendor and payment type seed tables
- indexes for common analytical queries
- full data load

Main tables:

```text
dim_vendor
dim_payment_type
dim_location
fact_trips
```

### SQL Analytics Layer

Completed SQL views:

```text
vw_daily_trip_summary
vw_hourly_demand
vw_borough_revenue
vw_zone_performance
vw_payment_summary
vw_ml_trip_features
```

These views support analytics, API endpoints, BI reporting, and ML feature generation.

### FastAPI Layer

Completed endpoints:

```text
GET  /
GET  /health
GET  /analytics/trips/summary
GET  /analytics/revenue/by-borough
GET  /analytics/demand/by-hour
GET  /analytics/zones/top-pickups
GET  /analytics/payments/summary
POST /predict/trip-duration
POST /predict/pretrip-duration
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

### Machine Learning Layer

Completed:

- analytical trip duration model
- pre-trip duration model
- model metrics output
- feature importance output
- local prediction script
- FastAPI prediction endpoints

Analytical model metrics:

```text
MAE:  1.35 minutes
RMSE: 3.40 minutes
R2:   0.9129
```

Pre-trip model metrics:

```text
MAE:  3.18 minutes
RMSE: 5.13 minutes
R2:   0.8094
```

### Testing

Completed automated tests:

```text
tests/test_transform_taxi_data.py
tests/test_api.py
```

Final test result:

```text
11 passed
```

Test coverage includes:

- column standardization
- invalid trip filtering
- time feature engineering
- financial feature engineering
- taxi zone enrichment
- FastAPI route registration
- prediction schema validation

### Documentation

Completed documentation:

```text
README.md
docs/project_overview.md
docs/data_dictionary.md
docs/database_design.md
docs/etl_design.md
docs/api_documentation.md
docs/ml_modeling.md
docs/dashboard_summary.md
docs/testing.md
```

## Final Validation Results

Final quality check passed.

Git status:

```text
nothing to commit, working tree clean
```

Test suite:

```text
11 passed
```

ETL pipeline:

```text
completed successfully
```

PostgreSQL quality checks:

```text
required null fields: 0
invalid business rule violations: 0
missing pickup location matches: 0
missing dropoff location matches: 0
missing payment type matches: 0
duplicate-like records: 0
```

Known data quality notes:

```text
missing passenger count: 1,768,022 rows
missing passenger count percentage: 16.98%
trips over 6 hours: 3,618
trips over 100 miles: 461
fares over $500: 89
```

These are documented as source-data quality notes and outliers rather than hidden or silently removed.

## Key Technical Decisions

### Preserve Raw Data

Raw input files are kept unchanged. Cleaned outputs are saved separately.

### Separate Profiling, Validation, and Transformation

Profiling describes the raw data, validation reports quality issues, and transformation creates cleaned analytics-ready data.

### Use PostgreSQL Fact and Dimension Modeling

The database uses `fact_trips` for trip-level facts and dimension tables for vendor, payment, and location reference data.

### Use SQL Views for Analytics

SQL views provide a reusable business logic layer for API endpoints, BI dashboards, and machine learning features.

### Build Two ML Models

The analytical model includes fare and total amount fields and performs strongly.

The pre-trip model excludes post-trip financial fields and is more realistic for operational prediction.

### Keep Tests Lightweight

Automated tests avoid requiring the full database or raw dataset so they can run quickly in local environments.

## Portfolio Summary

Enterprise Urban Mobility Data Platform | Python, PostgreSQL, FastAPI, Docker, Power BI

- Built an end-to-end data engineering platform that ingested 3 months of NYC Yellow Taxi trip records, profiled and validated raw data quality, transformed over 10 million records, and loaded analytics-ready tables into PostgreSQL.
- Designed a fact and dimension database model with SQL analytics views for daily trip trends, hourly demand, borough revenue, zone performance, payment summaries, and ML-ready feature generation.
- Developed FastAPI endpoints for analytics and trip duration prediction, including both analytical and pre-trip machine learning prediction workflows.
- Trained Random Forest regression models for taxi trip duration prediction, achieving 1.35-minute MAE for the analytical model and 3.18-minute MAE for the pre-trip model.
- Added automated unit tests for transformation logic and API schema validation, with 11 passing tests.

## Technical Highlights

This project demonstrates:

- profiling and validating raw operational data before transformation
- designing a modular ETL pipeline
- modeling analytical data with fact and dimension tables
- using SQL views as a reusable analytics layer
- exposing curated metrics through FastAPI
- identifying and explaining data leakage in machine learning
- comparing analytical and pre-trip prediction approaches
- documenting known data quality limitations transparently

## Current Project Status

The core data platform is complete and GitHub-ready.

Completed:

- ETL pipeline
- PostgreSQL database
- SQL analytics
- FastAPI API
- ML models
- automated tests
- documentation

Remaining future work:

- build Power BI dashboard on Windows
- add dashboard screenshots to README
- optionally add Airflow orchestration
- optionally add dbt models
- optionally add weather or holiday enrichment
- optionally add model monitoring and deployment improvements