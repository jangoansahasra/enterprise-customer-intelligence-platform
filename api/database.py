import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def get_database_url() -> str:
    """Build PostgreSQL connection URL from environment variables."""
    load_dotenv()

    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5433")
    db_name = os.getenv("DB_NAME", "urban_mobility_db")
    db_user = os.getenv("DB_USER", "urban_user")
    db_password = os.getenv("DB_PASSWORD", "urban_password")

    return f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def get_engine() -> Engine:
    """Create a SQLAlchemy engine for PostgreSQL."""
    return create_engine(get_database_url())