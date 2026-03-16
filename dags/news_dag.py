from datetime import datetime, timedelta
from airflow.decorators import task, dag
from pathlib import Path
import sys
import os

sys.path.insert(0, "/opt/airflow/src")

from extract_data import extract_data_
from load_data import load_data_
from transform_data import data_transformation_pipeline

env_path = Path(__file__).resolve().parents[1] / "config" / ".env"
from dotenv import load_dotenv

load_dotenv(env_path)
API_KEY = os.getenv("API")
url = f"https://gnews.io/api/v4/search?q=example&lang=en&country=us&max=70&apikey={API_KEY}"


@dag(
    dag_id='news_dag',
    default_args={
        'owner': 'airflow',
        'depends_on_past': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5)
        },
        description='A DAG to extract, transform and load news data',
        schedule='0 0 */1 * *',  # Run every day at midnight
        start_date=datetime(2026, 3, 1),
        catchup=False,tags=['news', 'etl']
)

def news_etl_pipeline():
    @task
    def extract():
        return extract_data_(url)

    @task
    def transform(_data):
        df = data_transformation_pipeline()
        df.to_parquet("/opt/airflow/data/news_data.parquet", index=False)
        return "/opt/airflow/data/news_data.parquet"

    @task
    def load(_parquet_path):
        import pandas as pd

        df = pd.read_parquet("/opt/airflow/data/news_data.parquet")
        table_name = "news_data"

        load_data_(table_name, df)

    extracted = extract()
    transformed = transform(extracted)
    load(transformed)
    # extracted >> transformed >> load

news_etl_pipeline()
