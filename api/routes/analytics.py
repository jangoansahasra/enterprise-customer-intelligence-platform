from typing import Any

from fastapi import APIRouter, Query
from sqlalchemy import text

from api.database import get_engine


router = APIRouter(prefix="/analytics", tags=["analytics"])


def fetch_all(query: str, params: dict[str, Any] | None = None) -> list[dict]:
    """Execute a SQL query and return rows as dictionaries."""
    engine = get_engine()

    with engine.connect() as connection:
        result = connection.execute(text(query), params or {})
        return [dict(row._mapping) for row in result]


@router.get("/trips/summary")
def get_trip_summary() -> dict:
    """Return executive summary metrics for loaded taxi trips."""
    query = """
        SELECT
            COUNT(*) AS total_trips,
            ROUND(SUM(total_amount), 2) AS total_revenue,
            ROUND(AVG(fare_amount), 2) AS avg_fare_amount,
            ROUND(AVG(trip_distance), 2) AS avg_trip_distance,
            ROUND(AVG(trip_duration_minutes), 2) AS avg_trip_duration_minutes,
            ROUND(AVG(tip_percentage), 2) AS avg_tip_percentage
        FROM fact_trips;
    """

    rows = fetch_all(query)
    return rows[0] if rows else {}


@router.get("/revenue/by-borough")
def get_revenue_by_borough(limit: int = Query(10, ge=1, le=100)) -> list[dict]:
    """Return top borough-to-borough revenue patterns."""
    query = """
        SELECT
            pickup_borough,
            COALESCE(NULLIF(dropoff_borough, ''), 'Unknown') AS dropoff_borough,
            total_trips,
            total_revenue,
            avg_total_amount,
            avg_trip_distance
        FROM vw_borough_revenue
        ORDER BY total_revenue DESC
        LIMIT :limit;
    """

    return fetch_all(query, {"limit": limit})


@router.get("/demand/by-hour")
def get_demand_by_hour() -> list[dict]:
    """Return trip demand grouped by pickup hour."""
    query = """
        SELECT
            pickup_hour,
            total_trips,
            total_revenue,
            avg_trip_distance,
            avg_trip_duration_minutes
        FROM vw_hourly_demand
        ORDER BY pickup_hour;
    """

    return fetch_all(query)


@router.get("/zones/top-pickups")
def get_top_pickup_zones(limit: int = Query(10, ge=1, le=100)) -> list[dict]:
    """Return top pickup zones by trip volume."""
    query = """
        SELECT
            pickup_borough,
            pickup_zone,
            pickup_trips,
            total_revenue,
            avg_total_amount,
            avg_trip_distance,
            avg_trip_duration_minutes
        FROM vw_zone_performance
        ORDER BY pickup_trips DESC
        LIMIT :limit;
    """

    return fetch_all(query, {"limit": limit})


@router.get("/payments/summary")
def get_payment_summary() -> list[dict]:
    """Return payment type summary metrics."""
    query = """
        SELECT
            COALESCE(payment_type_name, 'Unknown') AS payment_type_name,
            total_trips,
            total_revenue,
            avg_tip_amount,
            avg_tip_percentage
        FROM vw_payment_summary
        ORDER BY total_trips DESC;
    """

    return fetch_all(query)