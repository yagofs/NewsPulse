# News ETL Pipeline with Airflow

Simple technical portfolio project to demonstrate an end-to-end Data Engineering workflow: extract data from an API, transform it with Pandas, and load it into PostgreSQL, orchestrated by Apache Airflow.

## Project Goal

Build a small, production-style ETL pipeline that is:

- easy to run locally
- orchestrated with Airflow
- connected to PostgreSQL
- organized as modular Python code

## Architecture

- `extract`: fetches news data from GNews API and stores raw JSON in `data/data.json`
- `transform`: cleans and standardizes columns, converts timestamps to `America/Sao_Paulo`, writes Parquet
- `load`: inserts transformed data into PostgreSQL table `news_data`

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
│   └── airflow.cfg
├── newspulse/
│   ├── backend/server.py
│   ├── backend/requirements.txt
│   ├── Dockerfile
│   └── frontend/
├── docker-compose.yaml
├── main.py
└── requirements.txt
```

## Environment Variables

The ETL reads its variables from `config/.env`. Docker Compose also uses this file when started with the commands below.

Example `config/.env`:

```dotenv
API=YOUR_GNEWS_API_KEY
host=postgres
database=airflow
user=YOUR_POSTGRES_USER
password=YOUR_POSTGRES_PASSWORD
```

Keep real credentials private. For local Python execution, set `host` and the database credentials to a PostgreSQL instance accessible from your machine. The Docker Compose PostgreSQL service uses the database settings defined in `docker-compose.yaml`.

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

Set your GNews API key and PostgreSQL connection details.

### 4. Execute ETL

```bash
python main.py
```

## Run with Airflow + Docker

### 1. Start services

The Compose setup expects `config/.env` for its environment variables:

```bash
ENV_FILE_PATH=config/.env docker compose --env-file config/.env up -d
```

### 2. Open Airflow UI

URL: <http://localhost:8080>

### 3. Enable and run DAG

- Unpause `news_dag`.
- Trigger it manually or wait for its daily schedule (`0 0 */1 * *`).

## Access the NewsPulse Portal

The portal reads from PostgreSQL table `public.news_data`; it does not call GNews or run the ETL itself. Start the database and portal from the repository root:

```bash
ENV_FILE_PATH=config/.env docker compose --env-file config/.env up -d --build newspulse
```

Open <http://localhost:4173>. The table must already contain ETL data for news to appear. If it has not been populated yet, start the full Compose environment and run `news_dag` in Airflow as described above. The portal API is read-only; its health endpoint is <http://localhost:4173/api/health>.

## Expected Output

- Raw API payload: `data/data.json`
- Transformed dataset: `data/news_data.parquet`
- PostgreSQL table loaded: `news_data`
- NewsPulse portal: <http://localhost:4173>

## Common Issues (Troubleshooting)

### 1. `ModuleNotFoundError: No module named 'extract_data'`

Cause: `src` folder is not mounted in the Airflow container.
Fix: ensure Compose maps `./src:/opt/airflow/src`.

### 2. PostgreSQL connection refused inside Airflow

Cause: using `127.0.0.1` from inside a container.
Fix: use `host=postgres` in `config/.env` when running with Docker Compose.

### 3. Portal opens but shows no news or reports a database error

Cause: `public.news_data` may not exist yet, may be empty, or the portal database credentials may not match the PostgreSQL service.
Fix: confirm `config/.env` database settings, start the Compose services, then run `news_dag` in Airflow.

## Portfolio Notes

This project demonstrates:

- modular ETL design
- Airflow DAG orchestration with TaskFlow API
- practical Dockerized data platform setup
- a PostgreSQL-backed read-only news portal

## Next Improvements

- Add tests for transformation functions
- Add schema validation (e.g., Great Expectations or Pandera)
- Add incremental load / dedup strategy
- Add CI pipeline (lint + tests)
- Add data quality checks as Airflow tasks
