import requests
from src.mcp_server.config import MAPPLS_API_KEY, ROUTE_BASE_URL
from src.mcp_server.utils import latlng_to_lnglat


def get_route(origin: str, destination: str, traffic: bool = False):
    """
    Accepts origin/destination as 'lat,lng' from frontend,
    converts internally to 'lng,lat' for Mappls Routing API.
    """

    origin_norm = latlng_to_lnglat(origin)
    destination_norm = latlng_to_lnglat(destination)

    resource = "route_eta" if traffic else "route_adv"
    url = f"{ROUTE_BASE_URL}/{resource}/driving/{origin_norm};{destination_norm}"

    params = {
        "access_token": MAPPLS_API_KEY
    }

    print("ROUTE URL:", url)
    print("ROUTE PARAMS:", params)

    try:
        response = requests.get(url, params=params, timeout=20)
    except requests.RequestException as e:
        return {
            "ok": False,
            "tool": "get_route",
            "stage": "request",
            "url": url,
            "params": params,
            "error": str(e),
        }

    if response.status_code != 200:
        return {
            "ok": False,
            "tool": "get_route",
            "stage": "api_call",
            "url": response.url,
            "status_code": response.status_code,
            "response_text": response.text,
        }

    return {
        "ok": True,
        "tool": "get_route",
        "origin": origin,
        "destination": destination,
        "traffic": traffic,
        "data": response.json(),
    }