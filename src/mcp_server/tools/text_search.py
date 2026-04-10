import requests
from src.mcp_server.config import MAPPLS_API_KEY, SEARCH_BASE_URL


def text_search(query: str, location: str = "", top_k: int = 10):
    """
    Free-text place search.
    location: optional 'lat,lng'
    """
    url = url = "https://search.mappls.com/search/places/textsearch/json"

    params = {
        "query": query,
        "access_token": MAPPLS_API_KEY,
        "limit": top_k,
    }

    if location:
        params["location"] = location

    try:
        response = requests.get(url, params=params, timeout=20)
    except requests.RequestException as e:
        return {
            "ok": False,
            "tool": "text_search",
            "stage": "request",
            "url": url,
            "params": params,
            "error": str(e),
        }

    if response.status_code != 200:
        return {
            "ok": False,
            "tool": "text_search",
            "stage": "api_call",
            "url": url,
            "params": params,
            "status_code": response.status_code,
            "response_text": response.text,
        }

    data = response.json()
    results = data.get("suggestedLocations", []) or data.get("results", []) or []

    return {
        "ok": True,
        "tool": "text_search",
        "query": query,
        "location": location,
        "count": len(results),
        "results": results,
        "raw": data,
    }