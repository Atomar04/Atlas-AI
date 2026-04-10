import requests
from src.mcp_server.config import MAPPLS_API_KEY, SEARCH_BASE_URL


def get_place_details(eloc: str):
    """
    Fetch details for a Mappls eLoc / placeId.
    """
    url = f"https://place.mappls.com/O2O/entity/place-details/{eloc}"
    params = {"access_token": MAPPLS_API_KEY}

    try:
        response = requests.get(url, params=params, timeout=20)
    except requests.RequestException as e:
        return {
            "ok": False,
            "tool": "get_place_details",
            "stage": "request",
            "url": url,
            "params": params,
            "error": str(e),
        }

    if response.status_code != 200:
        return {
            "ok": False,
            "tool": "get_place_details",
            "stage": "api_call",
            "url": url,
            "params": params,
            "status_code": response.status_code,
            "response_text": response.text,
        }

    return {
        "ok": True,
        "tool": "get_place_details",
        "eloc": eloc,
        "data": response.json(),
    }