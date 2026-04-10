import requests
from src.mcp_server.config import MAPPLS_API_KEY, BASE_URL


def distance_matrix_eta(origin: str, destinations: list[str]):
    """
    origin: 'lat,lng'
    destinations: ['lat,lng', 'lat,lng', ...]
    Returns ETA-aware matrix, intended for traffic-sensitive ranking.
    """
    url = f"{BASE_URL}/advancedmaps/v1/{MAPPLS_API_KEY}/distance_matrix_eta"

    params = {
        "source": origin,
        "destination": "|".join(destinations),
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    data = response.json()

    return {
        "origin": origin,
        "destinations": destinations,
        "raw": data,
    }