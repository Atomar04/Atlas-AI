def get_place_details(place_id: str):
    """
    Fetch details of a place
    """
    url = f"{BASE_URL}/places/details"

    params = {
        "place_id": place_id,
        "key": MAPPLS_API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return {"error": "Details fetch failed"}

    return response.json()