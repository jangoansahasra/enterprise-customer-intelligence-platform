# Command Guide

This guide lists the main commands used to run and verify the Enterprise Urban Mobility Data Platform.

## Setup

Install Python dependencies:

```bash
make install
```

Start PostgreSQL with Docker Compose:

```bash
make start-db
```

Stop Docker services:

```bash
make stop-db
```

## Database Setup

Apply database schema, seed reference tables, indexes, and analytics views:

```bash
make schema
```

Apply or refresh only SQL analytics views:

```bash
make views
```

## ETL Pipeline

Run raw data profiling:

```bash
make profile
```

Run raw data validation:

```bash
make validate
```

Run taxi data transformation:

```bash
make transform
```

Run profiling, validation, and transformation together:

```bash
make etl
```

## PostgreSQL Loading

Load a 100,000-row sample into PostgreSQL:

```bash
make load-sample
```

Load the full cleaned dataset into PostgreSQL:

```bash
make load-full
```

## Data Quality

Run SQL data quality checks:

```bash
make quality
```

## API

Start the FastAPI server:

```bash
make api
```

API documentation is available locally at:

```text
http://127.0.0.1:8000/docs
```

## Machine Learning

Train the analytical trip duration model:

```bash
make train
```

Train the pre-trip duration prediction model:

```bash
make train-pretrip
```

## Testing

Run all tests:

```bash
make test
```

## Common Local Workflow

A typical local workflow is:

```bash
make start-db
make schema
make etl
make load-full
make quality
make test
make api
```

The API can then be tested from:

```text
http://127.0.0.1:8000/docs
```