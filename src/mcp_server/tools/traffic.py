def get_traffic(lat: float, lng: float):
    """
    Fetch real-time traffic at a location
    """
    url = f"{BASE_URL}/traffic"

    params = {
        "location": f"{lat},{lng}",
        "key": MAPPLS_API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return {"error": "Traffic fetch failed"}

    return response.json()