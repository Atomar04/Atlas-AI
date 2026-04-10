import os
from dotenv import load_dotenv

load_dotenv()

MAPPLS_API_KEY = os.getenv("MAPPLS_API_KEY")

BASE_URL = "https://atlas.mappls.com/api"