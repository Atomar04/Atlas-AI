import os
from dotenv import load_dotenv

load_dotenv()

MAPPLS_API_KEY = os.getenv("MAPPLS_API_KEY", "")

# Keep these generic for now.
# once auth is fixed, just adjust the exact endpoint paths if needed.
BASE_URL = os.getenv("MAPPLS_BASE_URL", "https://atlas.mappls.com/api")
SEARCH_BASE_URL = os.getenv("MAPPLS_SEARCH_BASE_URL", "https://atlas.mappls.com/api")
GEOCODE_BASE_URL = os.getenv("MAPPLS_GEOCODE_BASE_URL", "https://search.mappls.com/search/address/geocode")