# API Documentation

## Overview

The FastAPI layer exposes analytics from the PostgreSQL urban mobility database.

The API reads from SQL analytics views and fact/dimension tables created from cleaned NYC Yellow Taxi trip data.

## Run Locally

Start PostgreSQL with Docker Compose:

```bash
docker compose up -d