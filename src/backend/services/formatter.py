def format_response(query, center, places, session_id=None, previous_query=None):
    """
    Formats backend response into frontend-ready structure
    """

    normalized_places = []

    for i, p in enumerate(places):
        normalized_places.append({
            "id": p.get("id", f"place_{i+1}"),
            "rank": i + 1,
            "name": p["name"],
            "lat": p["lat"],
            "lng": p["lng"],
            "rating": p.get("rating"),
            "distance_km": p.get("distance"),  # standardize name
            "address": p.get("address"),
            "category": p.get("category", "place"),
            "open_now": p.get("open_now")
        })

    top_place = normalized_places[0] if normalized_places else None

    summary = (
        f"Found {len(normalized_places)} places. "
        f"Top result is {top_place['name']} "
        f"({top_place.get('rating', 'N/A')}⭐, "
        f"{top_place.get('distance_km', 'N/A')} km away)."
        if top_place else "No results found."
    )

    return {
        "query": query,

        "center": center,

        "places": normalized_places,

        "summary": summary,

        "map_actions": {
            "type": "SHOW_RESULTS",
            "zoom": 14,
            "highlight_top_k": 5
        },

        "interaction_hints": [
            "Tap a place to see directions",
            "Say 'take me to the third one'"
        ],

        "context": {
            "session_id": session_id,
            "previous_query": previous_query
        }
    }