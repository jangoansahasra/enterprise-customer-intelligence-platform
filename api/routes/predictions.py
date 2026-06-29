from pathlib import Path

import joblib
import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "ml" / "models" / "trip_duration_model.joblib"

router = APIRouter(prefix="/predict", tags=["predictions"])


class TripDurationPredictionRequest(BaseModel):
    pickup_hour: int = Field(..., ge=0, le=23)
    pickup_day_of_week: str
    pickup_month: int = Field(..., ge=1, le=12)
    is_weekend: bool
    passenger_count: float | None = Field(default=None, ge=0)
    trip_distance: float = Field(..., gt=0)
    fare_amount: float = Field(..., gt=0)
    total_amount: float = Field(..., gt=0)
    pickup_borough: str
    dropoff_borough: str
    payment_type_id: int = Field(..., ge=0)


class TripDurationPredictionResponse(BaseModel):
    predicted_trip_duration_minutes: float


def load_model():
    """Load trained trip duration model."""
    if not MODEL_PATH.exists():
        raise HTTPException(
            status_code=404,
            detail="Model file not found. Run python ml/train_model.py first.",
        )

    return joblib.load(MODEL_PATH)


@router.post("/trip-duration", response_model=TripDurationPredictionResponse)
def predict_trip_duration(
    request: TripDurationPredictionRequest,
) -> TripDurationPredictionResponse:
    """Predict taxi trip duration in minutes."""
    model = load_model()

    input_df = pd.DataFrame([request.model_dump()])
    prediction = model.predict(input_df)[0]

    return TripDurationPredictionResponse(
        predicted_trip_duration_minutes=round(float(prediction), 2)
    )