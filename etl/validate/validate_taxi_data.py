from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
REPORT_DIR = PROJECT_ROOT / "data" / "validation_reports"

SUMMARY_REPORT_PATH = REPORT_DIR / "taxi_data_validation_summary.csv"
INVALID_SAMPLE_PATH = REPORT_DIR / "taxi_data_invalid_records_sample.csv"

VALID_PAYMENT_TYPES = {1, 2, 3, 4, 5, 6}
SAMPLE_LIMIT_PER_RULE = 100


def load_zone_lookup_ids() -> set[int]:
    """Load valid taxi zone LocationIDs from the lookup table."""
    lookup_path = RAW_DATA_DIR / "taxi_zone_lookup.csv"

    if not lookup_path.exists():
        raise FileNotFoundError(f"Taxi zone lookup file not found: {lookup_path}")

    lookup_df = pd.read_csv(lookup_path)
    return set(lookup_df["LocationID"].dropna().astype(int))


def add_validation_result(
    results: list[dict],
    dataset: str,
    rule_name: str,
    invalid_count: int,
    total_rows: int,
    severity: str,
    description: str,
) -> None:
    """Append one validation rule result."""
    invalid_percentage = round((invalid_count / total_rows) * 100, 4) if total_rows else 0

    results.append(
        {
            "dataset": dataset,
            "rule_name": rule_name,
            "severity": severity,
            "invalid_count": int(invalid_count),
            "total_rows": int(total_rows),
            "invalid_percentage": invalid_percentage,
            "description": description,
        }
    )


def collect_invalid_sample(
    samples: list[pd.DataFrame],
    df: pd.DataFrame,
    mask: pd.Series,
    dataset: str,
    rule_name: str,
) -> None:
    """Collect a small sample of invalid rows for inspection."""
    invalid_rows = df.loc[mask].head(SAMPLE_LIMIT_PER_RULE).copy()

    if invalid_rows.empty:
        return

    invalid_rows.insert(0, "rule_name", rule_name)
    invalid_rows.insert(0, "dataset", dataset)
    samples.append(invalid_rows)


def validate_file(
    file_path: Path,
    valid_location_ids: set[int],
    results: list[dict],
    samples: list[pd.DataFrame],
) -> None:
    """Run validation checks against one raw taxi Parquet file."""
    dataset = file_path.name
    print(f"Validating {dataset}...")

    df = pd.read_parquet(file_path)
    total_rows = len(df)

    validation_rules = [
        {
            "rule_name": "missing_pickup_datetime",
            "severity": "critical",
            "mask": df["tpep_pickup_datetime"].isna(),
            "description": "Pickup timestamp is missing.",
        },
        {
            "rule_name": "missing_dropoff_datetime",
            "severity": "critical",
            "mask": df["tpep_dropoff_datetime"].isna(),
            "description": "Dropoff timestamp is missing.",
        },
        {
            "rule_name": "dropoff_before_pickup",
            "severity": "critical",
            "mask": df["tpep_dropoff_datetime"] < df["tpep_pickup_datetime"],
            "description": "Dropoff timestamp occurs before pickup timestamp.",
        },
        {
            "rule_name": "non_positive_trip_distance",
            "severity": "high",
            "mask": df["trip_distance"] <= 0,
            "description": "Trip distance is zero or negative.",
        },
        {
            "rule_name": "non_positive_fare_amount",
            "severity": "high",
            "mask": df["fare_amount"] <= 0,
            "description": "Fare amount is zero or negative.",
        },
        {
            "rule_name": "negative_total_amount",
            "severity": "high",
            "mask": df["total_amount"] < 0,
            "description": "Total amount is negative.",
        },
        {
            "rule_name": "negative_passenger_count",
            "severity": "medium",
            "mask": df["passenger_count"] < 0,
            "description": "Passenger count is negative.",
        },
        {
            "rule_name": "missing_passenger_count",
            "severity": "medium",
            "mask": df["passenger_count"].isna(),
            "description": "Passenger count is missing.",
        },
        {
            "rule_name": "invalid_payment_type",
            "severity": "medium",
            "mask": ~df["payment_type"].isin(VALID_PAYMENT_TYPES),
            "description": "Payment type is outside expected TLC code values.",
        },
        {
            "rule_name": "missing_pickup_location_id",
            "severity": "critical",
            "mask": df["PULocationID"].isna(),
            "description": "Pickup location ID is missing.",
        },
        {
            "rule_name": "missing_dropoff_location_id",
            "severity": "critical",
            "mask": df["DOLocationID"].isna(),
            "description": "Dropoff location ID is missing.",
        },
        {
            "rule_name": "pickup_location_not_in_lookup",
            "severity": "high",
            "mask": ~df["PULocationID"].isin(valid_location_ids),
            "description": "Pickup location ID is not found in taxi zone lookup.",
        },
        {
            "rule_name": "dropoff_location_not_in_lookup",
            "severity": "high",
            "mask": ~df["DOLocationID"].isin(valid_location_ids),
            "description": "Dropoff location ID is not found in taxi zone lookup.",
        },
        {
            "rule_name": "extreme_trip_duration_over_6_hours",
            "severity": "medium",
            "mask": (
                (
                    df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]
                ).dt.total_seconds()
                / 60
            )
            > 360,
            "description": "Trip duration is greater than 6 hours.",
        },
        {
            "rule_name": "extreme_trip_distance_over_100_miles",
            "severity": "medium",
            "mask": df["trip_distance"] > 100,
            "description": "Trip distance is greater than 100 miles.",
        },
        {
            "rule_name": "extreme_fare_amount_over_500",
            "severity": "medium",
            "mask": df["fare_amount"] > 500,
            "description": "Fare amount is greater than 500 dollars.",
        },
    ]

    for rule in validation_rules:
        mask = rule["mask"].fillna(False)
        invalid_count = int(mask.sum())

        add_validation_result(
            results=results,
            dataset=dataset,
            rule_name=rule["rule_name"],
            invalid_count=invalid_count,
            total_rows=total_rows,
            severity=rule["severity"],
            description=rule["description"],
        )

        collect_invalid_sample(
            samples=samples,
            df=df,
            mask=mask,
            dataset=dataset,
            rule_name=rule["rule_name"],
        )


def main() -> None:
    """Run validation checks and save validation reports."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    valid_location_ids = load_zone_lookup_ids()
    parquet_files = sorted(RAW_DATA_DIR.glob("yellow_tripdata_*.parquet"))

    if not parquet_files:
        raise FileNotFoundError(f"No yellow taxi Parquet files found in {RAW_DATA_DIR}")

    results: list[dict] = []
    samples: list[pd.DataFrame] = []

    for file_path in parquet_files:
        validate_file(file_path, valid_location_ids, results, samples)

    summary_df = pd.DataFrame(results)
    summary_df.to_csv(SUMMARY_REPORT_PATH, index=False)

    if samples:
        sample_df = pd.concat(samples, ignore_index=True)
        sample_df.to_csv(INVALID_SAMPLE_PATH, index=False)

    print("\nTaxi data validation complete.")
    print(f"Summary report saved to: {SUMMARY_REPORT_PATH}")

    if samples:
        print(f"Invalid record sample saved to: {INVALID_SAMPLE_PATH}")


if __name__ == "__main__":
    main()