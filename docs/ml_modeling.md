# Machine Learning Modeling

## Overview

This project includes a machine learning layer for predicting NYC yellow taxi trip duration.

The target variable is:

```text
trip_duration_minutes
```

The models are trained from the PostgreSQL analytics view:

```text
vw_ml_trip_features
```

This demonstrates that the ML workflow uses the cleaned and database-ready analytics layer rather than directly training from raw files.

## Training Data Source

Training data is loaded from PostgreSQL using SQLAlchemy.

Source view:

```sql
vw_ml_trip_features
```

The view joins trip facts with pickup and dropoff location dimensions and exposes ML-ready fields.

## Target Variable

```text
trip_duration_minutes
```

This value is calculated during the transformation step using pickup and dropoff timestamps.

## Model Versions

### Analytical Duration Model

The analytical model uses both trip characteristics and post-trip financial fields.

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

Performance:

```text
MAE:  1.35 minutes
RMSE: 3.40 minutes
R2:   0.9129
```

Metrics and feature importance are saved to:

```text
ml/models/trip_duration_metrics.json
ml/models/trip_duration_feature_importance.csv
```

This model performs very well, but it includes `fare_amount` and `total_amount`, which are usually only known after a trip is completed.

### Pre-Trip Duration Model

The pre-trip model removes post-trip financial fields to reduce data leakage.

Features include:

```text
pickup_hour
pickup_day_of_week
pickup_month
is_weekend
passenger_count
trip_distance
pickup_borough
dropoff_borough
payment_type_id
```

Excluded post-trip fields:

```text
fare_amount
total_amount
tip_amount
```

Performance:

```text
MAE:  3.18 minutes
RMSE: 5.13 minutes
R2:   0.8094
```

Metrics and feature importance are saved to:

```text
ml/models/pretrip_duration_metrics.json
ml/models/pretrip_duration_feature_importance.csv
```

This model is more realistic for pre-trip prediction. It performs slightly worse than the analytical model, but it avoids relying on information that would not be available before a trip starts.

## Model Pipeline

Both models use a scikit-learn `RandomForestRegressor`.

The training pipeline includes:

- median imputation for numeric features
- most-frequent imputation for categorical features
- standard scaling for numeric features
- one-hot encoding for categorical features
- random forest regression model

## Training Sample

Both model versions train on a sample of:

```text
250,000 rows
```

This keeps training practical on a laptop while still using a large real-world sample.

## Feature Importance

Feature importance is exported for both models.

Top features from the analytical model:

```text
fare_amount
trip_distance
pickup_hour
total_amount
pickup_borough
```

Top features from the pre-trip model:

```text
trip_distance
pickup_hour
pickup_borough
dropoff_borough
passenger_count
```

## Interpretation

The analytical model has stronger metrics because it uses fare-related fields that are highly correlated with duration.

The pre-trip model is more realistic because it excludes post-trip financial fields and relies mostly on route distance, pickup time, and location features.

This contrast demonstrates awareness of data leakage and prediction-time feature availability.

## Run Training

Analytical model:

```bash
python ml/train_model.py
```

Pre-trip model:

```bash
python ml/train_pretrip_model.py
```

These create local model artifacts:

```text
ml/models/trip_duration_model.joblib
ml/models/pretrip_duration_model.joblib
```

Generated model artifacts are ignored by Git and can be recreated by running the training scripts.

## Run Prediction

Analytical prediction script:

```bash
python ml/predict.py
```

Example output:

```text
Predicted trip duration: 21.57 minutes
```

## API Prediction Endpoint

The analytical trained model is exposed through FastAPI:

```text
POST /predict/trip-duration
```

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

## Future Improvements

Potential improvements include:

- expose the pre-trip model through FastAPI
- compare Linear Regression, Random Forest, and XGBoost
- tune hyperparameters for both model versions
- train on a larger sample or full dataset
- add model monitoring for prediction drift
- add Power BI visuals for model metrics and feature importance