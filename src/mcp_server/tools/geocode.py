import requests
from src.mcp_server.config import MAPPLS_API_KEY, GEOCODE_BASE_URL

def geocode_address(address: str):
    """
    Converts an address string into geographic coordinates
    """

    params = {
        "address": address,
        "access_token": MAPPLS_API_KEY
    }

    response = requests.get(GEOCODE_BASE_URL, params=params)

    if response.status_code != 200:
        return {
            "error": "Geocoding failed",
            "status_code": response.status_code,
            "response_text": response.text
        }

    return response.json()