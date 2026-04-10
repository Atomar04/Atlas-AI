import requests
from src.mcp_server.config import MAPPLS_API_KEY, BASE_URL


def get_traffic(lat: float, lng: float):
    """
    Fetch traffic information for a location.
    """
    url = f"{BASE_URL}/traffic"

    params = {
        "location": f"{lat},{lng}",
        "access_token": MAPPLS_API_KEY,
    }

    try:
        response = requests.get(url, params=params, timeout=20)
    except requests.RequestException as e:
        return {
            "ok": False,
            "tool": "get_traffic",
            "stage": "request",
            "url": url,
            "params": params,
            "error": str(e),
        }

    if response.status_code != 200:
        return {
            "ok": False,
            "tool": "get_traffic",
            "stage": "api_call",
            "url": url,
            "params": params,
            "status_code": response.status_code,
            "response_text": response.text,
        }

    return {
        "ok": True,
        "tool": "get_traffic",
        "location": f"{lat},{lng}",
        "data": response.json(),
    }