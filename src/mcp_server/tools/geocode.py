import requests
from src.mcp_server.config import MAPPLS_API_KEY, BASE_URL

def geocode_address(address: str):
    """
    Converts an address string into latitude & longitude
    """
    url = f"{BASE_URL}/places/geocode"
    
    params = {
        "address": address,
        "key": MAPPLS_API_KEY
    }

    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        return {"error": "Geocoding failed"}

    return response.json()