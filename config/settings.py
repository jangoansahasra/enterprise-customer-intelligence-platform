import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
VALIDATION_REPORTS_DIR = DATA_DIR / "validation_reports"

ZONE_LOOKUP_PATH = RAW_DATA_DIR / "taxi_zone_lookup.csv"
CLEANED_TRIPS_PATH = PROCESSED_DATA_DIR / "cleaned_taxi_trips_2025_q1.parquet"

LOGS_DIR = PROJECT_ROOT / "logs"

ML_DIR = PROJECT_ROOT / "ml"
MODEL_DIR = ML_DIR / "models"

DATABASE_DIR = PROJECT_ROOT / "database"
SQL_DIR = PROJECT_ROOT / "sql"

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")
DB_NAME = os.getenv("DB_NAME", "urban_mobility_db")
DB_USER = os.getenv("DB_USER", "urban_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "urban_password")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

LOAD_SAMPLE_SIZE = int(os.getenv("LOAD_SAMPLE_SIZE", "100000"))