import requests
from src.mcp_server.config import MAPPLS_API_KEY, GEOCODE_BASE_URL


def geocode_address(address: str):
    """
    Convert a free-text address into coordinates / matched place data.
    """

    params = {
        "address": address,
        "access_token": MAPPLS_API_KEY,
    }

    try:
        response = requests.get(GEOCODE_BASE_URL, params=params, timeout=20)
    except requests.RequestException as e:
        return {
            "ok": False,
            "tool": "geocode_address",
            "stage": "request",
            "error": str(e),
            "params": params,
        }

    if response.status_code != 200:
        return {
            "ok": False,
            "tool": "geocode_address",
            "stage": "api_call",
            "status_code": response.status_code,
            "params": params,
            "response_text": response.text,
        }

    return {
        "ok": True,
        "tool": "geocode_address",
        "query": address,
        "data": response.json(),
    }