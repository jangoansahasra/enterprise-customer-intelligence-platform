import pandas as pd

from etl.transform.transform_taxi_data import (
    add_financial_features,
    add_time_features,
    enrich_with_zones,
    filter_invalid_rows,
    standardize_column_names,
)


def test_standardize_column_names() -> None:
    df = pd.DataFrame(
        {
            "VendorID": [1],
            "RatecodeID": [1],
            "PULocationID": [236],
            "DOLocationID": [237],
            "Passenger Count": [1],
        }
    )

    result = standardize_column_names(df)

    assert "vendor_id" in result.columns
    assert "ratecode_id" in result.columns
    assert "pickup_location_id" in result.columns
    assert "dropoff_location_id" in result.columns
    assert "passenger_count" in result.columns


def test_filter_invalid_rows_removes_bad_records() -> None:
    df = pd.DataFrame(
        {
            "tpep_pickup_datetime": pd.to_datetime(
                [
                    "2025-01-01 10:00:00",
                    "2025-01-01 10:00:00",
                    "2025-01-01 10:00:00",
                    "2025-01-01 10:00:00",
                    "2007-12-05 18:45:00",
                ]
            ),
            "tpep_dropoff_datetime": pd.to_datetime(
                [
                    "2025-01-01 10:20:00",
                    "2025-01-01 09:50:00",
                    "2025-01-01 10:20:00",
                    "2025-01-01 10:20:00",
                    "2007-12-05 19:02:00",
                ]
            ),
            "trip_distance": [3.0, 3.0, 0.0, 3.0, 3.0],
            "fare_amount": [18.0, 18.0, 18.0, -5.0, 18.0],
            "total_amount": [24.0, 24.0, 24.0, 24.0, 24.0],
            "pickup_location_id": [236, 236, 236, 236, 236],
            "dropoff_location_id": [237, 237, 237, 237, 237],
        }
    )

    result = filter_invalid_rows(df)

    assert len(result) == 1
    assert result.iloc[0]["trip_distance"] == 3.0
    assert result.iloc[0]["fare_amount"] == 18.0


def test_add_time_features() -> None:
    df = pd.DataFrame(
        {
            "tpep_pickup_datetime": pd.to_datetime(["2025-01-04 14:30:00"]),
            "tpep_dropoff_datetime": pd.to_datetime(["2025-01-04 15:00:00"]),
        }
    )

    result = add_time_features(df)

    assert result.loc[0, "trip_duration_minutes"] == 30.0
    assert result.loc[0, "pickup_hour"] == 14
    assert result.loc[0, "pickup_month"] == 1
    assert result.loc[0, "pickup_day_of_week"] == "Saturday"
    assert bool(result.loc[0, "is_weekend"]) is True


def test_add_financial_features() -> None:
    df = pd.DataFrame(
        {
            "fare_amount": [20.0, 0.0],
            "trip_distance": [4.0, 2.0],
            "tip_amount": [5.0, 3.0],
        }
    )

    result = add_financial_features(df)

    assert result.loc[0, "fare_per_mile"] == 5.0
    assert result.loc[0, "tip_percentage"] == 25.0
    assert result.loc[1, "tip_percentage"] == 0.0


def test_enrich_with_zones_adds_pickup_and_dropoff_details() -> None:
    trips_df = pd.DataFrame(
        {
            "pickup_location_id": [236],
            "dropoff_location_id": [237],
        }
    )

    zone_df = pd.DataFrame(
        {
            "location_id": [236, 237],
            "borough": ["Manhattan", "Manhattan"],
            "zone": ["Upper East Side North", "Upper East Side South"],
            "service_zone": ["Yellow Zone", "Yellow Zone"],
        }
    )

    result = enrich_with_zones(trips_df, zone_df)

    assert result.loc[0, "pickup_borough"] == "Manhattan"
    assert result.loc[0, "pickup_zone"] == "Upper East Side North"
    assert result.loc[0, "dropoff_borough"] == "Manhattan"
    assert result.loc[0, "dropoff_zone"] == "Upper East Side South"