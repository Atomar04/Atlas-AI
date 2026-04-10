import requests


class MCPClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip("/")

    def _post(self, path: str, payload: dict):
        url = f"{self.base_url}{path}"
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()

    def geocode(self, address: str):
        return self._post("/tool/geocode", {"address": address})

    def nearby(self, lat: float, lng: float, keyword: str, radius: int = 3000):
        return self._post(
            "/tool/nearby",
            {
                "lat": lat,
                "lng": lng,
                "keyword": keyword,
                "radius": radius,
            },
        )

    def route(self, origin: str, destination: str):
        return self._post(
            "/tool/route",
            {
                "origin": origin,
                "destination": destination,
            },
        )

    def traffic(self, route_id: str):
        return self._post("/tool/traffic", {"route_id": route_id})

    def place_details(self, place_id: str):
        return self._post("/tool/place_details", {"place_id": place_id})

    def text_search(self, query: str, location: str = "", top_k: int = 10):
        return self._post(
            "/tool/text_search",
            {
                "query": query,
                "location": location,
                "top_k": top_k,
            },
        )

    def distance_matrix(self, origin: str, destinations: list[str]):
        return self._post(
            "/tool/distance_matrix",
            {
                "origin": origin,
                "destinations": destinations,
            },
        )

    def distance_matrix_eta(self, origin: str, destinations: list[str]):
        return self._post(
            "/tool/distance_matrix_eta",
            {
                "origin": origin,
                "destinations": destinations,
            },
        )