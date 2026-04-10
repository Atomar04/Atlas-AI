import requests
from src.mcp_server.config import MAPPLS_API_KEY, SEARCH_BASE_URL


def search_nearby(lat: float, lng: float, keyword: str, radius: int = 1000):
    """
    Find nearby places around a coordinate.
    """
    url = "https://search.mappls.com/search/places/nearby/json"
    params = {
        "keywords": keyword,
        "refLocation": f"{lat},{lng}",
        "radius": radius,
        "access_token": MAPPLS_API_KEY,
    }

    try:
        response = requests.get(url, params=params, timeout=20)
    except requests.RequestException as e:
        return {
            "ok": False,
            "tool": "search_nearby",
            "stage": "request",
            "url": url,
            "params": params,
            "error": str(e),
        }

    if response.status_code != 200:
        return {
            "ok": False,
            "tool": "search_nearby",
            "stage": "api_call",
            "url": url,
            "params": params,
            "status_code": response.status_code,
            "response_text": response.text,
        }

    data = response.json()
    results = data.get("suggestedLocations", []) or data.get("results", []) or data.get("places", []) or []

    return {
        "ok": True,
        "tool": "search_nearby",
        "location": f"{lat},{lng}",
        "keyword": keyword,
        "radius": radius,
        "count": len(results),
        "results": results,
        "raw": data,
    }