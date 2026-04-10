import requests
from src.mcp_server.config import MAPPLS_API_KEY, BASE_URL

def search_nearby(lat: float, lng: float, keyword: str):
    """
    Finds nearby places based on keyword
    """
    url = f"{BASE_URL}/places/nearby"

    params = {
        "location": f"{lat},{lng}",
        "keyword": keyword,
        "key": MAPPLS_API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return {"error": "Nearby search failed"}

    return response.json()