from pathlib import Path

import joblib
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "ml" / "models" / "trip_duration_model.joblib"


def predict_trip_duration(input_data: dict) -> float:
    """Predict trip duration in minutes for one trip."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model file not found: {MODEL_PATH}. Run python ml/train_model.py first."
        )

    model = joblib.load(MODEL_PATH)
    input_df = pd.DataFrame([input_data])
    prediction = model.predict(input_df)[0]

    return round(float(prediction), 2)


def main() -> None:
    """Run a sample trip duration prediction."""
    sample_trip = {
        "pickup_hour": 14,
        "pickup_day_of_week": "Wednesday",
        "pickup_month": 1,
        "is_weekend": False,
        "passenger_count": 1,
        "trip_distance": 3.2,
        "fare_amount": 18.5,
        "total_amount": 24.3,
        "pickup_borough": "Manhattan",
        "dropoff_borough": "Manhattan",
        "payment_type_id": 1,
    }

    predicted_duration = predict_trip_duration(sample_trip)

    print("Sample trip input:")
    print(sample_trip)
    print(f"\nPredicted trip duration: {predicted_duration} minutes")


if __name__ == "__main__":
    main()