from io import StringIO

import pandas as pd
from sqlalchemy import create_engine, text

from config.settings import (
    CLEANED_TRIPS_PATH,
    DATABASE_URL,
    LOAD_SAMPLE_SIZE,
    ZONE_LOOKUP_PATH,
)


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

    if LOAD_SAMPLE_SIZE > 0:
        df = df.head(LOAD_SAMPLE_SIZE)
        print(f"Using sample load size: {LOAD_SAMPLE_SIZE:,} rows")

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
    """Load fact trip records into PostgreSQL using COPY for faster bulk inserts."""
    fact_df = prepare_fact_trips()

    print(f"Loading {len(fact_df):,} rows into fact_trips...")

    columns = list(fact_df.columns)
    column_list = ", ".join(columns)

    raw_connection = engine.raw_connection()

    try:
        with raw_connection.cursor() as cursor:
            for start in range(0, len(fact_df), chunk_size):
                end = start + chunk_size
                chunk = fact_df.iloc[start:end]

                buffer = StringIO()
                chunk.to_csv(buffer, index=False, header=False, na_rep="\\N")
                buffer.seek(0)

                copy_sql = f"""
                    COPY fact_trips ({column_list})
                    FROM STDIN
                    WITH (FORMAT CSV, NULL '\\N')
                """

                cursor.copy_expert(copy_sql, buffer)
                raw_connection.commit()

                print(f"Loaded rows {start + 1:,} to {min(end, len(fact_df)):,}")

    except Exception:
        raw_connection.rollback()
        raise

    finally:
        raw_connection.close()

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

    engine = create_engine(DATABASE_URL)

    clear_existing_data(engine)
    load_dim_location(engine)
    load_fact_trips(engine)

    print("\nPostgreSQL load complete.")


if __name__ == "__main__":
    main()