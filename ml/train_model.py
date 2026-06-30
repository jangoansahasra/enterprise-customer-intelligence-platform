import json

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sqlalchemy import create_engine

from config.settings import DATABASE_URL, MODEL_DIR


MODEL_PATH = MODEL_DIR / "trip_duration_model.joblib"
METRICS_PATH = MODEL_DIR / "trip_duration_metrics.json"
FEATURE_IMPORTANCE_PATH = MODEL_DIR / "trip_duration_feature_importance.csv"

SAMPLE_SIZE = 250_000
RANDOM_STATE = 42


def load_training_data() -> pd.DataFrame:
    query = f"""
        SELECT
            pickup_hour,
            pickup_day_of_week,
            pickup_month,
            is_weekend,
            passenger_count,
            trip_distance,
            fare_amount,
            total_amount,
            pickup_borough,
            dropoff_borough,
            payment_type_id,
            trip_duration_minutes
        FROM vw_ml_trip_features
        WHERE trip_duration_minutes > 0
          AND trip_duration_minutes <= 180
          AND trip_distance > 0
        LIMIT {SAMPLE_SIZE};
    """

    engine = create_engine(DATABASE_URL)
    return pd.read_sql(query, engine)


def build_model() -> Pipeline:
    numeric_features = [
        "pickup_hour",
        "pickup_month",
        "passenger_count",
        "trip_distance",
        "fare_amount",
        "total_amount",
        "payment_type_id",
    ]

    categorical_features = [
        "pickup_day_of_week",
        "is_weekend",
        "pickup_borough",
        "dropoff_borough",
    ]

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_features),
            ("categorical", categorical_pipeline, categorical_features),
        ]
    )

    model = RandomForestRegressor(
        n_estimators=80,
        max_depth=18,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )


def main() -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading training data from PostgreSQL...")
    df = load_training_data()
    print(f"Loaded training rows: {len(df):,}")

    target = "trip_duration_minutes"
    X = df.drop(columns=[target])
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=RANDOM_STATE,
    )

    model = build_model()

    print("Training trip duration model...")
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = mean_squared_error(y_test, predictions) ** 0.5
    r2 = r2_score(y_test, predictions)

    print("\nModel evaluation:")
    print(f"MAE:  {mae:.2f} minutes")
    print(f"RMSE: {rmse:.2f} minutes")
    print(f"R2:   {r2:.4f}")

    metrics = {
        "model": "RandomForestRegressor",
        "training_rows": int(len(df)),
        "test_size": 0.2,
        "target": target,
        "mae_minutes": round(float(mae), 2),
        "rmse_minutes": round(float(rmse), 2),
        "r2": round(float(r2), 4),
        "features": list(X.columns),
    }

    with open(METRICS_PATH, "w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=4)

    print(f"Metrics saved to: {METRICS_PATH}")

    preprocessor = model.named_steps["preprocessor"]
    trained_model = model.named_steps["model"]

    feature_names = preprocessor.get_feature_names_out()
    feature_importance_df = pd.DataFrame(
        {
            "feature": feature_names,
            "importance": trained_model.feature_importances_,
        }
    ).sort_values(by="importance", ascending=False)

    feature_importance_df.to_csv(FEATURE_IMPORTANCE_PATH, index=False)
    print(f"Feature importance saved to: {FEATURE_IMPORTANCE_PATH}")

    joblib.dump(model, MODEL_PATH)
    print(f"\nModel saved to: {MODEL_PATH}")


if __name__ == "__main__":
    main()