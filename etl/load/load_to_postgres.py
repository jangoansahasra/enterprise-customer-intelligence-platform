import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"

ZONE_LOOKUP_PATH = RAW_DATA_DIR / "taxi_zone_lookup.csv"
CLEANED_TRIPS_PATH = PROCESSED_DATA_DIR / "cleaned_taxi_trips_2025_q1.parquet"


def get_database_url() -> str:
    """Build PostgreSQL connection URL from environment variables."""
    load_dotenv()

    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5433")
    db_name = os.getenv("DB_NAME", "urban_mobility_db")
    db_user = os.getenv("DB_USER", "urban_user")
    db_password = os.getenv("DB_PASSWORD", "urban_password")

    return f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def load_dim_location(engine) -> None:
    """Load taxi zone lookup data into dim_location."""
    print("Loading dim_location...")

    location_df = pd.read_csv(ZONE_LOOKUP_PATH)
    location_df = location_df.rename(
        columns={
            "LocationID": "location_id",
            "Borough": "borough",
            "Zone": "zone",
            "service_zone": "service_zone",
        }
    )

    location_df.to_sql(
        "dim_location",
        engine,
        if_exists="append",
        index=False,
        method="multi",
    )

    print(f"Loaded {len(location_df):,} rows into dim_location.")


def prepare_fact_trips() -> pd.DataFrame:
    """Prepare cleaned taxi data for fact_trips table."""
    print("Reading cleaned taxi trips...")

    df = pd.read_parquet(CLEANED_TRIPS_PATH)

    sample_size = int(os.getenv("LOAD_SAMPLE_SIZE", "100000"))
    if sample_size > 0:
        df = df.head(sample_size)
        print(f"Using sample load size: {sample_size:,} rows")

    fact_columns = {
        "vendor_id": "vendor_id",
        "payment_type": "payment_type_id",
        "pickup_location_id": "pickup_location_id",
        "dropoff_location_id": "dropoff_location_id",
        "tpep_pickup_datetime": "pickup_datetime",
        "tpep_dropoff_datetime": "dropoff_datetime",
        "passenger_count": "passenger_count",
        "trip_distance": "trip_distance",
        "ratecode_id": "ratecode_id",
        "store_and_fwd_flag": "store_and_fwd_flag",
        "fare_amount": "fare_amount",
        "extra": "extra",
        "mta_tax": "mta_tax",
        "tip_amount": "tip_amount",
        "tolls_amount": "tolls_amount",
        "improvement_surcharge": "improvement_surcharge",
        "total_amount": "total_amount",
        "congestion_surcharge": "congestion_surcharge",
        "airport_fee": "airport_fee",
        "cbd_congestion_fee": "cbd_congestion_fee",
        "trip_duration_minutes": "trip_duration_minutes",
        "pickup_date": "pickup_date",
        "pickup_hour": "pickup_hour",
        "pickup_day_of_week": "pickup_day_of_week",
        "pickup_month": "pickup_month",
        "is_weekend": "is_weekend",
        "fare_per_mile": "fare_per_mile",
        "tip_percentage": "tip_percentage",
    }

    fact_df = df[list(fact_columns.keys())].rename(columns=fact_columns)

    fact_df["vendor_id"] = fact_df["vendor_id"].astype("Int64")
    fact_df["payment_type_id"] = fact_df["payment_type_id"].astype("Int64")
    fact_df["pickup_location_id"] = fact_df["pickup_location_id"].astype("Int64")
    fact_df["dropoff_location_id"] = fact_df["dropoff_location_id"].astype("Int64")
    fact_df["pickup_date"] = pd.to_datetime(fact_df["pickup_date"]).dt.date

    return fact_df


def load_fact_trips(engine, chunk_size: int = 100_000) -> None:
    """Load fact trip records into PostgreSQL in chunks."""
    fact_df = prepare_fact_trips()

    print(f"Loading {len(fact_df):,} rows into fact_trips...")

    fact_df.to_sql(
        "fact_trips",
        engine,
        if_exists="append",
        index=False,
        chunksize=chunk_size,
        method="multi",
    )

    print("Loaded fact_trips successfully.")


def clear_existing_data(engine) -> None:
    """Clear fact and location data before reload."""
    print("Clearing existing fact/location data...")

    with engine.begin() as connection:
        connection.execute(text("TRUNCATE TABLE fact_trips RESTART IDENTITY;"))
        connection.execute(text("TRUNCATE TABLE dim_location CASCADE;"))


def main() -> None:
    """Load processed taxi data into PostgreSQL."""
    if not CLEANED_TRIPS_PATH.exists():
        raise FileNotFoundError(
            f"Cleaned data file not found: {CLEANED_TRIPS_PATH}. "
            "Run python -m etl.pipeline first."
        )

    database_url = get_database_url()
    engine = create_engine(database_url)

    clear_existing_data(engine)
    load_dim_location(engine)
    load_fact_trips(engine)

    print("\nPostgreSQL load complete.")


if __name__ == "__main__":
    main()