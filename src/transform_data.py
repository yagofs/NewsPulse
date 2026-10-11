import pandas as pd
import json
from pathlib import Path
import logging  

logging.basicConfig(level=logging.INFO)


path_name = Path(__file__).parent.parent / 'data' / 'data.json'
# Keep these fields in the transformed dataset so the portal can read them
# from PostgreSQL. The load step adds the columns to existing tables when needed.
columns_to_drop = []
columns_name_to_rename = {
    'id': 'news_id',
    'title': 'news_title',
    'description': 'news_description',
    'url': 'news_url',
    'publishedAt': 'news_published_at',
    'langs': 'language',
    'source.id': 'source_id',
    'source.name': 'source_name',
    'source.url': 'source_url',
    'source.country': 'source_country',
}

def create_detaframe(path_name: Path) -> pd.DataFrame:
    path = path_name

    if not path.exists():
        logging.error(f"File {path} does not exist.")
        return pd.DataFrame()  # Return an empty DataFrame if the file doesn't exist
    
    try:
        with open(path) as f:
            data = json.load(f)
            data.pop('information', None)  # Remove 'information' key if it exists
        
        df = pd.json_normalize(
            data, 
            record_path=['articles'],
            meta=['totalArticles']
        )
        logging.info(f"Data successfully loaded into DataFrame from {path}")
        return df 
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from file {path}: {e}")
        return pd.DataFrame()  # Return an empty DataFrame if JSON is invalid
    

def drop_columns(df: pd.DataFrame, columns_to_drop:list) -> pd.DataFrame:
    df = df.drop(columns=columns_to_drop, errors='ignore')

    logging.info(f"Columns {columns_to_drop} dropped from DataFrame")
    return df


def transform_data_to_br(df:pd.DataFrame) -> pd.DataFrame:
    if 'publishedAt' not in df.columns:
        logging.warning("Column 'publishedAt' not found in DataFrame. Skipping date transformation.")
        return df

    df['publishedAt'] = pd.to_datetime(df['publishedAt'])
    df['publishedAt'] = df['publishedAt'].dt.tz_convert('America/Sao_Paulo')

    df['publishedAt_br'] = df['publishedAt'].dt.strftime('%d/%m/%Y %H:%M:%S')

    logging.info("Date transformed to Brazilian timezone and format")
    return df


def rename_columns(df: pd.DataFrame, columns_name_to_rename:dict) -> pd.DataFrame:
    df = df.rename(columns=columns_name_to_rename)

    logging.info(f"Columns renamed according to columns to rename")
    return df


def data_transformation_pipeline():
    print("Starting data transformation pipeline...")
    df = create_detaframe(path_name)
    if df.empty:
        logging.error("DataFrame is empty. Exiting transformation pipeline.")
        return df
    df = drop_columns(df, columns_to_drop)
    df = transform_data_to_br(df)
    df = rename_columns(df, columns_name_to_rename)
    logging.info("Data transformation pipeline completed successfully.")
    return df
