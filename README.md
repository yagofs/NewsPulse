# News ETL Pipeline with Airflow

Simple technical portfolio project to demonstrate an end-to-end Data Engineering workflow:
extract data from an API, transform it with Pandas, and load it into PostgreSQL, orchestrated by Apache Airflow.

## Project Goal

Build a small, production-style ETL pipeline that is:
- easy to run locally
- orchestrated with Airflow
- connected to PostgreSQL
- organized as modular Python code

## Architecture

1. `extract`: fetches news data from GNews API and stores raw JSON in `data/data.json`
2. `transform`: cleans and standardizes columns, converts timestamps to `America/Sao_Paulo`, writes parquet
3. `load`: inserts transformed data into PostgreSQL table `news_data`

Airflow DAG: `dags/news_dag.py`  
Core ETL modules: `src/extract_data.py`, `src/transform_data.py`, `src/load_data.py`

## Tech Stack

- Python 3.14
- Pandas
- SQLAlchemy + psycopg2
- PostgreSQL
- Apache Airflow 3.1.8 (CeleryExecutor)
- Docker + Docker Compose

## Repository Structure

```text
.
├── dags/
│   └── news_dag.py
├── src/
│   ├── extract_data.py
│   ├── transform_data.py
│   └── load_data.py
├── data/
│   ├── data.json
│   └── news_data.parquet
├── config/
│   ├── .env
│   └── airflow.cfg
├── docker-compose.yaml
├── main.py
└── requirements.txt
```

## Environment Variables

This project uses two `.env` files:

1. Root `.env` (used by Docker Compose / Airflow containers)
2. `config/.env` (used by ETL Python modules)

### Example: root `.env`

```env
AIRFLOW_UID=1000
host=postgres
database=airflow
user=airflow
password=airflow
```

### Example: `config/.env`

```env
API=YOUR_GNEWS_API_KEY
host=postgres
database=airflow
user=airflow
password=airflow
```

If running ETL outside Docker (local Python only), change `config/.env` database credentials to your local PostgreSQL instance.

## Run Locally (without Airflow)

### 1. Create and activate virtual environment

```bash
python -m venv eng
source eng/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure `config/.env`

Set your API key and database credentials.

### 4. Execute ETL

```bash
python main.py
```

## Run with Airflow + Docker

### 1. Start services

```bash
docker compose up -d
```

### 2. Open Airflow UI

- URL: `http://localhost:8080`
- Default credentials (from official compose template): `airflow` / `airflow`

### 3. Enable and run DAG

1. Unpause `news_dag`
2. Trigger manually or wait for schedule (`0 0 */1 * *`)

## Expected Output

- Raw API payload: `data/data.json`
- Transformed dataset: `data/news_data.parquet`
- PostgreSQL table loaded: `news_data`

## Common Issues (Troubleshooting)

### 1. `ModuleNotFoundError: No module named 'extract_data'`

Cause: `src` folder not mounted in Airflow container.  
Fix: ensure compose volume maps `./src:/opt/airflow/src`.

### 2. DAG runs with success but no task instances

Cause: `start_date` set in the future.  
Fix: set DAG `start_date` to a past date.

### 3. `Permission denied` in `airflow-init` on Fedora

Cause: SELinux context on mounted folders.  
Fix: use `:z` suffix in Docker volume mounts and proper `AIRFLOW_UID`.

### 4. PostgreSQL connection refused inside Airflow

Cause: using `127.0.0.1` from inside container.  
Fix: use `host=postgres` in `config/.env` when running with Docker Compose.

### 5. `Ident authentication failed`

Cause: PostgreSQL auth method configured as `ident/peer`.  
Fix: update `pg_hba.conf` to `scram-sha-256` or `md5` for localhost host rules.

## Portfolio Notes

This project demonstrates:
- modular ETL design
- Airflow DAG orchestration with TaskFlow API
- practical Dockerized data platform setup
- real-world debugging of environment, auth, import, and scheduling issues

## Next Improvements

- Add tests for transformation functions
- Add schema validation (e.g., Great Expectations or Pandera)
- Add incremental load / dedup strategy
- Add CI pipeline (lint + tests)
- Add data quality checks as Airflow tasks

