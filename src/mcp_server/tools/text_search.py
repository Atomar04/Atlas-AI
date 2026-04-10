import requests
from src.mcp_server.config import MAPPLS_API_KEY, SEARCH_BASE_URL


def text_search(query: str, location: str = "", top_k: int = 10):
    """
    Free-text place search for queries like:
    - 'heritage sites in Mysuru'
    - 'best biryani in Hyderabad'
    - 'Apollo hospitals Chennai'
    """
    url = f"{SEARCH_BASE_URL}/places/textsearch/json"

    params = {
        "query": query,
        "access_token": MAPPLS_API_KEY,
        "limit": top_k,
    }

    if location:
        params["location"] = location

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    data = response.json()

    # Keep output backend-friendly and stable
    results = data.get("suggestedLocations", []) or data.get("results", []) or []

    return {
        "query": query,
        "location": location,
        "count": len(results),
        "results": results,
        "raw": data,
    }