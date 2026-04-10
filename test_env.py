import os
from dotenv import load_dotenv

load_dotenv()

MAPPLS_API_KEY = os.getenv("MAPPLS_API_KEY")
print("MAPPLS_API_KEY loaded:", bool(MAPPLS_API_KEY))