from src.extract_data import extract_data_
from src.load_data import load_data_
from src.transform_data import data_transformation_pipeline

import os
from pathlib import Path
from dotenv import load_dotenv


import logging
logging.basicConfig(level=logging.INFO)

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / "config" / ".env"
load_dotenv(ENV_PATH)

API_KEY = os.getenv('API')

url = f'https://gnews.io/api/v4/search?q=example&lang=en&country=us&max=15&apikey={API_KEY}'

table_name = 'news_data'

def pipeline():
    try:
        logging.info("Starting ETL pipeline.: EXTRACT")
        extract_data_(url)

        logging.info("fase 2: TRANSFORM")
        df = data_transformation_pipeline()

        logging.info("fase 3: LOAD")
        load_data_(table_name, df)

        logging.info("ETL pipeline completed successfully.")
    except Exception as e:
        logging.error(f"An error occurred during the ETL pipeline: {e}")
        import traceback
        traceback.print_exc()


pipeline()
