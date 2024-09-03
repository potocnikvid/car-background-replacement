import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

API_MODE = os.getenv("API_MODE", "demo")
API_KEY = os.getenv("API_KEY", "")

RESULT_MODE = 'fg-image-shadow'
OPTIONS = {
    'demo': {
        'url': f'https://demo.api4ai.cloud/img-bg-removal/v1/cars/results?mode={RESULT_MODE}',
        'headers': {'A4A-CLIENT-APP-ID': 'sample'}
    }
}
