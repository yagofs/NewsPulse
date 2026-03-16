import requests
import json
from pathlib import Path
import logging
import os 
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / "config" / ".env"
load_dotenv(ENV_PATH)

API_KEY = os.getenv('API')
url = f'https://gnews.io/api/v4/search?q=example&lang=en&country=us&max=10&apikey={API_KEY}'

def extract_data_(url:str) -> list:

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        output_path = Path("data/data.json")
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(data, f, indent=4)

        logging.info(f"Data successfully extracted and saved to {output_path}")
        return data
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching data: {e}")
        return []
    

if __name__ == "__main__":
    extract_data(url)
