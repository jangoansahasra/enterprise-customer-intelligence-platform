from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from config.settings import DATABASE_URL


def get_engine() -> Engine:
    """Create a SQLAlchemy engine for PostgreSQL."""
    return create_engine(DATABASE_URL)