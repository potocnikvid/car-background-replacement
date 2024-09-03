import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file


# Use 'demo' mode just to try api4ai for free. Free demo is rate limited.
# For more details visit:
#   https://api4.ai
#
# Use 'rapidapi' if you want to try api4ai via RapidAPI marketplace.
# For more details visit:
#   https://rapidapi.com/api4ai-api4ai-default/api/cars-image-background-removal/details

API_MODE = os.getenv("API_MODE", "demo")
API_KEY = os.getenv("API_KEY", "")

# Your RapidAPI key. Fill this variable with the proper value if you want
# to try api4ai via RapidAPI marketplace.

# Processing mode influences returned result. Supported values are:
# * fg-image-shadow - Foreground image with shadow added.
# * fg-image - Foreground image.
# * fg-mask - Mask image.
API_RESULT_MODE = os.getenv("API_RESULT_MODE", 'fg-image-shadow')

API_OPTIONS = {
    'demo': {
        'url': f'https://demo.api4ai.cloud/img-bg-removal/v1/cars/results?mode={API_RESULT_MODE}',
        'headers': {'A4A-CLIENT-APP-ID': 'sample'}
    },
    'rapidapi': {
        'url': f'https://cars-image-background-removal.p.rapidapi.com/v1/results?mode={API_RESULT_MODE}',
        'headers': {'X-RapidAPI-Key': API_KEY}
    }
}



