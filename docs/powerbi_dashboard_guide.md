# Power BI Dashboard Guide

## Overview

The Power BI dashboard connects to the PostgreSQL analytics layer of the Enterprise Urban Mobility Data Platform.

The dashboard is designed to help transportation analysts and decision-makers understand taxi demand, revenue patterns, zone performance, payment behavior, and machine learning model results.

## Data Source

Power BI should connect directly to PostgreSQL.

Connection details for local development:

```text
Server: localhost
Port: 5433
Database: urban_mobility_db
Username: urban_user
Password: urban_password
```

## Recommended Power BI connection:
```text
PostgreSQL database connector
Import mode
```

Import mode is recommended because the dataset is large and dashboard interactions will be faster.

## PostgreSQL Views Used

The dashboard should primarily use these analytics views:
```text
vw_daily_trip_summary
vw_hourly_demand
vw_borough_revenue
vw_zone_performance
vw_payment_summary
vw_ml_trip_features
```

These views are created from cleaned PostgreSQL fact and dimension tables.

## Dashboard Page 1: Executive Overview

Purpose:
Show high-level transportation activity and revenue performance.
Recommended visuals:
. KPI card: total trips
. KPI card: total revenue
. KPI card: average fare amount
. KPI card: average trip distance
. KPI card: average trip duration
. KPI card: average tip percentage
. Line chart: total trips by pickup date
. Line chart: total revenue by pickup date
. Bar chart: total revenue by pickup borough
. Bar chart: total trips by pickup borough

## Recommended source views:
```text
vw_daily_trip_summary
vw_borough_revenue
```
## Dashboard Page 2: Demand Patterns

Purpose:
Analyze when taxi demand is highest.
Recommended visuals:

. Column chart: trips by pickup hour
. Column chart: trips by day of week
. Line chart: trips by pickup date
. Bar chart: trips by pickup borough
. Donut chart: weekday vs weekend trips

Recommended source views:
```text
vw_hourly_demand
vw_daily_trip_summary
vw_zone_performance
vw_ml_trip_features
```
## Dashboard Page 3: Revenue And Payment Insights
Purpose:
Analyze revenue, fares, tips, and payment behavior.
Recommended visuals:
. Bar chart: revenue by pickup borough
. Bar chart: revenue by pickup/dropoff borough pair
. Donut chart: trips by payment type
. Bar chart: total revenue by payment type
. KPI card: average total amount
. KPI card: average tip percentage
. Line chart: revenue trend by pickup date

Recommended source views:
```text
vw_borough_revenue
vw_payment_summary
vw_daily_trip_summary
```
## Dashboard Page 4: Zone Performance

Purpose:
Understand which taxi zones generate the most demand and revenue.
Recommended visuals:

. Table: top pickup zones by trips
. Table: top pickup zones by revenue
. Bar chart: top pickup zones by total trips
. Bar chart: top pickup zones by total revenue
. Scatter plot: average trip distance vs average trip duration by pickup zone
. Map visual: pickup zones or boroughs if geographic fields are available

Recommended source views:
```text
vw_zone_performance
```
## Dashboard Page 5: ML Insights
Purpose:
Show model performance and explain key prediction drivers.
Recommended visuals:

. KPI card: analytical model MAE
. KPI card: analytical model RMSE
. KPI card: analytical model R2
. KPI card: pre-trip model MAE
. KPI card: pre-trip model RMSE
. KPI card: pre-trip model R2
. Bar chart: analytical model feature importance
. Bar chart: pre-trip model feature importance

Recommended source files:
```text
ml/models/trip_duration_metrics.json
ml/models/trip_duration_feature_importance.csv
ml/models/pretrip_duration_metrics.json
ml/models/pretrip_duration_feature_importance.csv
```
## Suggested Dashboard Filters
Recommended slicers:

- pickup date
- pickup month
- pickup day of week
- pickup hour
- pickup borough
- dropoff borough
- payment type
- weekend vs weekday
- Dashboard Design Notes
- Use a clean operational analytics style.

Recommended layout:

- KPI cards at the top
- trend visuals in the middle
- detailed tables at the bottom
- consistent colors for boroughs and payment types
- simple titles that explain the metric clearly
- Avoid making the dashboard look like a marketing page. It should look like a transportation operations dashboard.

## Expected Dashboard Outcomes
- The dashboard should help answer:
- How many taxi trips occurred during the selected period?
- Which days and hours had the highest demand?
- Which boroughs and zones generated the most revenue?
- Which payment methods were used most often?
- Which locations had longer or more expensive trips?
- How accurate are the trip duration prediction models?
- Which features influenced model predictions most?

## Future Dashboard Enhancements
Potential enhancements include:

- weather and holiday impact analysis
- model monitoring visuals
- prediction error trends
- pickup/dropoff route analysis
- borough-level comparison pages
- incremental monthly reporting