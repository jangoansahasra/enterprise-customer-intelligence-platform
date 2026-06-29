# Project Design Overview

## Enterprise Urban Mobility Data Platform

The Enterprise Urban Mobility Data Platform is an end-to-end data engineering and analytics project built around NYC Yellow Taxi trip data.

The project simulates a transportation agency data platform that converts raw operational taxi records into trusted, queryable, analytics-ready, API-accessible, and machine-learning-ready data.

## Business Context

City transportation agencies receive large volumes of trip records every month. These raw records contain useful information about demand, revenue, geography, payment behavior, trip distance, and trip duration, but the raw files are not immediately ready for business analysis.

A transportation analytics team may need to answer questions such as:

- which pickup and dropoff zones have the highest taxi demand
- which boroughs generate the most revenue
- how trip demand changes by hour, weekday, and month
- which zone-to-zone patterns appear most often
- how payment type and trip distance relate to revenue
- whether machine learning can estimate trip duration from trip characteristics

This project addresses that problem by designing a complete data platform around the NYC TLC trip dataset.

## Data Sources

The platform uses official NYC Taxi & Limousine Commission data.

Raw trip files:

```text
yellow_tripdata_2025-01.parquet
yellow_tripdata_2025-02.parquet
yellow_tripdata_2025-03.parquet
```

Lookup file:

```text
taxi_zone_lookup.csv
```

The trip files contain taxi trip-level operational data such as pickup/dropoff timestamps, trip distance, fare amounts, payment type, passenger count, and pickup/dropoff location IDs.

The taxi zone lookup file maps location IDs to readable borough, zone, and service zone information.

## System Architecture

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
FastAPI Analytics and Prediction API
        ↓
Machine Learning Models
        ↓
Power BI Dashboard Preparation
```

The architecture separates raw data, validation logic, transformation logic, database storage, SQL analytics, API access, and machine learning workflows.

## ETL Workflow

The ETL workflow is organized into modular Python components.

```text
etl/
├── profile/
├── validate/
├── transform/
├── load/
└── pipeline.py
```

### Profiling

The profiling module inspects raw datasets and records:

- row counts
- column counts
- data types
- missing values
- duplicate rows
- numeric statistics
- memory usage
- date ranges
- suspicious values

### Validation

The validation module checks business and data quality rules, including:

- missing pickup or dropoff timestamps
- dropoff timestamps before pickup timestamps
- non-positive trip distance
- non-positive fare amount
- negative total amount
- invalid payment types
- missing location IDs
- location IDs not found in the taxi zone lookup table
- duplicate-like trip records
- extreme duration, distance, and fare outliers

### Transformation

The transformation step standardizes and enriches the raw trip data.

Derived fields include:

```text
trip_duration_minutes
pickup_date
pickup_hour
pickup_day_of_week
pickup_month
is_weekend
fare_per_mile
tip_percentage
```

The transformation also joins pickup and dropoff location details from the taxi zone lookup file.

Final cleaned dataset:

```text
10,413,054 rows
34 columns
```

## Database Layer

PostgreSQL is used as the analytical database.

The database follows a fact and dimension structure:

```text
dim_vendor
dim_payment_type
dim_location
fact_trips
```

The `fact_trips` table stores cleaned trip-level records. Dimension tables provide descriptive reference data for vendors, payment types, and locations.

This structure supports analytics, BI reporting, and machine learning feature generation.

## SQL Analytics Layer

The SQL layer creates reusable analytics views:

```text
vw_daily_trip_summary
vw_hourly_demand
vw_borough_revenue
vw_zone_performance
vw_payment_summary
vw_ml_trip_features
```

These views make it easier for downstream tools to query business-ready metrics without repeatedly writing complex joins or aggregations.

Example use cases:

- daily trip and revenue trends
- demand by pickup hour
- revenue by borough pair
- top pickup zones
- payment type summaries
- ML-ready feature extraction

## API Layer

FastAPI exposes analytics and prediction results through REST endpoints.

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

The API allows application users, dashboards, or external systems to access curated analytics without directly querying the database.

FastAPI also provides interactive Swagger/OpenAPI documentation at:

```text
http://127.0.0.1:8000/docs
```

## Machine Learning Layer

The project includes two machine learning workflows for trip duration prediction.

### Analytical Trip Duration Model

The first model uses trip, location, payment, fare, and total amount features.

This model achieved:

```text
MAE:  1.35 minutes
RMSE: 3.40 minutes
R2:   0.9129
```

This model performs strongly, but includes post-trip financial fields such as fare amount and total amount.

### Pre-Trip Duration Model

The second model excludes post-trip financial fields such as:

```text
fare_amount
total_amount
tip_amount
```

This makes it more realistic for prediction before or at pickup time.

This model achieved:

```text
MAE:  3.18 minutes
RMSE: 5.13 minutes
R2:   0.8094
```

The pre-trip model has lower performance than the analytical model, but it is more realistic for operational use.

## Data Quality Strategy

The platform handles data quality in multiple layers:

- profiling identifies raw data patterns and suspicious values
- validation reports rule violations before transformation
- transformation filters critical invalid records
- PostgreSQL constraints and foreign keys enforce relational integrity
- SQL data quality checks verify the loaded database tables

After the final full load:

```text
fact_trips: 10,413,054 rows
required null fields: 0
invalid business rule violations: 0
missing foreign key matches: 0
duplicate-like records: 0
```

Known remaining quality notes:

- some trips have missing passenger count
- some extreme but valid outliers remain
- monthly TLC files include a small number of boundary records near month edges

## Design Decisions

Key design decisions include:

- using official NYC TLC data instead of a small synthetic dataset
- storing raw data unchanged and writing cleaned data separately
- using Parquet for efficient local storage
- separating profiling, validation, transformation, and loading logic
- modeling PostgreSQL tables with fact and dimension design
- using SQL views for reusable analytics
- exposing analytics through FastAPI instead of only SQL queries
- training ML models from the database analytics layer instead of directly from raw files
- keeping generated large artifacts out of Git where appropriate

## Current Project Status

Completed:

- raw data ingestion
- raw data profiling
- data validation
- data transformation
- processed Parquet output
- PostgreSQL schema design
- full PostgreSQL load
- SQL analytics views
- SQL data quality checks
- FastAPI analytics endpoints
- trip duration ML model
- pre-trip duration ML model
- FastAPI prediction endpoints
- README documentation
- API documentation
- ML documentation

Planned:

- Power BI dashboard
- dashboard documentation
- optional orchestration with Airflow
- optional transformation layer with dbt
- optional weather or holiday enrichment
- optional model monitoring and drift tracking

## Technical Highlights

This project demonstrates an end-to-end urban mobility data platform that processes over 10 million NYC taxi trip records, validates and transforms raw operational data, loads analytics-ready tables into PostgreSQL, creates SQL views for reporting, exposes insights through FastAPI, and trains machine learning models for trip duration prediction.

Key technical highlights:

- raw data is preserved unchanged for reproducibility
- data validation improves trust before transformation
- fact and dimension tables support analytics and BI use cases
- SQL views simplify reporting, API access, and ML feature generation
- FastAPI exposes curated analytics without requiring direct database access
- post-trip features can inflate ML performance
- the pre-trip model is more realistic for operational prediction