from fastapi import FastAPI
from sqlalchemy import text

from api.database import get_engine
from api.routes.analytics import router as analytics_router


app = FastAPI(
    title="Enterprise Urban Mobility Data Platform API",
    description="Analytics API for NYC yellow taxi trip data.",
    version="1.0.0",
)

app.include_router(analytics_router)


@app.get("/")
def root() -> dict:
    """Return API welcome message."""
    return {
        "message": "Enterprise Urban Mobility Data Platform API",
        "docs": "/docs",
    }


@app.get("/health")
def health_check() -> dict:
    """Check API and database connectivity."""
    engine = get_engine()

    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "status": "healthy",
        "database": "connected",
    }