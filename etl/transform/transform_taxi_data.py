from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

OUTPUT_PATH = PROCESSED_DATA_DIR / "cleaned_taxi_trips_2025_q1.parquet"
MIN_VALID_DATETIME = pd.Timestamp("2024-12-31")
MAX_VALID_DATETIME = pd.Timestamp("2025-04-03 23:59:59")


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize raw TLC column names to snake_case."""
    column_mapping = {
        "VendorID": "vendor_id",
        "RatecodeID": "ratecode_id",
        "PULocationID": "pickup_location_id",
        "DOLocationID": "dropoff_location_id",
    }

    df = df.rename(columns=column_mapping)
    df.columns = (
        df.columns.str.strip()
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
        .str.lower()
    )

    return df


def load_zone_lookup() -> pd.DataFrame:
    """Load taxi zone lookup table with standardized column names."""
    lookup_path = RAW_DATA_DIR / "taxi_zone_lookup.csv"
    zone_df = pd.read_csv(lookup_path)

    zone_df = zone_df.rename(
        columns={
            "LocationID": "location_id",
            "Borough": "borough",
            "Zone": "zone",
            "service_zone": "service_zone",
        }
    )

    return zone_df


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create time-based analytics features."""
    df["trip_duration_minutes"] = (
        df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]
    ).dt.total_seconds() / 60

    df["pickup_date"] = df["tpep_pickup_datetime"].dt.date
    df["pickup_hour"] = df["tpep_pickup_datetime"].dt.hour
    df["pickup_day_of_week"] = df["tpep_pickup_datetime"].dt.day_name()
    df["pickup_month"] = df["tpep_pickup_datetime"].dt.month
    df["is_weekend"] = df["tpep_pickup_datetime"].dt.dayofweek >= 5

    return df


def add_financial_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create fare and tip analytics features."""
    df["fare_per_mile"] = df["fare_amount"] / df["trip_distance"]

    df["tip_percentage"] = 0.0
    positive_fare_mask = df["fare_amount"] > 0
    df.loc[positive_fare_mask, "tip_percentage"] = (
        df.loc[positive_fare_mask, "tip_amount"]
        / df.loc[positive_fare_mask, "fare_amount"]
    ) * 100

    return df


def filter_invalid_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Remove critical and high-severity invalid records."""
    valid_mask = (
        df["tpep_pickup_datetime"].notna()
        & df["tpep_dropoff_datetime"].notna()
        & (df["tpep_dropoff_datetime"] >= df["tpep_pickup_datetime"])
        & (df["trip_distance"] > 0)
        & (df["fare_amount"] > 0)
        & (df["total_amount"] >= 0)
        & df["pickup_location_id"].notna()
        & df["dropoff_location_id"].notna()
        & (df["tpep_pickup_datetime"] >= MIN_VALID_DATETIME)
        & (df["tpep_pickup_datetime"] <= MAX_VALID_DATETIME)
        & (df["tpep_dropoff_datetime"] >= MIN_VALID_DATETIME)
        & (df["tpep_dropoff_datetime"] <= MAX_VALID_DATETIME)
    )

    return df.loc[valid_mask].copy()


def enrich_with_zones(df: pd.DataFrame, zone_df: pd.DataFrame) -> pd.DataFrame:
    """Add pickup and dropoff borough/zone details."""
    pickup_zones = zone_df.add_prefix("pickup_")
    dropoff_zones = zone_df.add_prefix("dropoff_")

    df = df.merge(
        pickup_zones,
        left_on="pickup_location_id",
        right_on="pickup_location_id",
        how="left",
    )

    df = df.merge(
        dropoff_zones,
        left_on="dropoff_location_id",
        right_on="dropoff_location_id",
        how="left",
    )

    return df


def transform_taxi_data() -> pd.DataFrame:
    """Transform raw taxi trip files into one cleaned analytics dataset."""
    parquet_files = sorted(RAW_DATA_DIR.glob("yellow_tripdata_*.parquet"))

    if not parquet_files:
        raise FileNotFoundError(f"No yellow taxi Parquet files found in {RAW_DATA_DIR}")

    transformed_files = []
    zone_df = load_zone_lookup()

    for file_path in parquet_files:
        print(f"Transforming {file_path.name}...")

        df = pd.read_parquet(file_path)
        original_rows = len(df)

        df = standardize_column_names(df)
        df = filter_invalid_rows(df)
        df = add_time_features(df)
        df = add_financial_features(df)
        df = enrich_with_zones(df, zone_df)

        print(f"Rows kept from {file_path.name}: {len(df):,} of {original_rows:,}")
        transformed_files.append(df)

    cleaned_df = pd.concat(transformed_files, ignore_index=True)

    return cleaned_df


def main() -> None:
    """Run taxi data transformation and save cleaned dataset."""
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    cleaned_df = transform_taxi_data()
    cleaned_df.to_parquet(OUTPUT_PATH, index=False)

    print("\nTaxi data transformation complete.")
    print(f"Cleaned rows: {len(cleaned_df):,}")
    print(f"Cleaned dataset saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()