import requests
from src.mcp_server.config import MAPPLS_API_KEY, BASE_URL

def get_route(start: str, end: str):
    """
    Returns route between two coordinates
    """
    url = f"{BASE_URL}/routing"

    params = {
        "start": start,
        "end": end,
        "key": MAPPLS_API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return {"error": "Routing failed"}

    return response.json()