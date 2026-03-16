from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
import pandas as pd
from pathlib import Path
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)

BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / "config" / ".env"
load_dotenv(ENV_PATH)

def _clean_env(value: str | None) -> str | None:
    if value is None:
        return None
    return value.strip().strip("'").strip('"')

user = _clean_env(os.getenv("user"))
password = _clean_env(os.getenv("password"))
database = _clean_env(os.getenv("database"))
host = _clean_env(os.getenv("host")) or "localhost"

def get_engine():
    logging.info("Creating database engine...")

    if not password or not user or not database:
        logging.error("Database credentials are not set in environment variables.")
        raise ValueError("Database credentials are missing.")
    
    url = URL.create(
        drivername="postgresql+psycopg2",
        username=user,
        password=password,
        host=host,
        port=5432,
        database=database,
    )

    return create_engine(url)

engine = get_engine()

def load_data_(table_name:str, df: pd.DataFrame):
    try:
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists='append',
            index=False
        )
        logging.info(f"Data successfully loaded into {table_name} table.")

        df_check = pd.read_sql_query(text(f"SELECT * FROM {table_name}"), con=engine)
        logging.info(f"total of records in {table_name}: {len(df_check)}")
    except Exception as e:
        logging.error(f"Error loading data: {e}")
        raise
