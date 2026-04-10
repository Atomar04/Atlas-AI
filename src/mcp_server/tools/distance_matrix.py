import requests
from src.mcp_server.config import MAPPLS_API_KEY, ROUTE_BASE_URL
from src.mcp_server.utils import latlng_to_lnglat


def distance_matrix(origin: str, destinations: list[str]):
    """
    Accepts origin/destinations as 'lat,lng',
    converts internally to 'lng,lat' for Mappls matrix API.
    """
    origin_norm = latlng_to_lnglat(origin)
    destinations_norm = [latlng_to_lnglat(d) for d in destinations]

    joined_points = ";".join([origin_norm] + destinations_norm)
    url = f"{ROUTE_BASE_URL}/dm/distance_matrix/driving/{joined_points}"

    params = {
        "access_token": MAPPLS_API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=20)
    except requests.RequestException as e:
        return {
            "ok": False,
            "tool": "get_distance_matrix",
            "stage": "request",
            "url": url,
            "params": params,
            "error": str(e),
        }

    if response.status_code != 200:
        return {
            "ok": False,
            "tool": "get_distance_matrix",
            "stage": "api_call",
            "url": url,
            "params": params,
            "status_code": response.status_code,
            "response_text": response.text,
        }

    return {
        "ok": True,
        "tool": "get_distance_matrix",
        "origin": origin,
        "destinations": destinations,
        "traffic": False,
        "data": response.json(),
    }