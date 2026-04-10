# src/backend/services/ranking_service.py

def get_weights(query):
    """
    Returns dynamic weights based on query intent
    """

    q = query.lower()

    # NEAREST → prioritize distance & time
    if "nearest" in q:
        return {
            "speed": 0.4,
            "distance": 0.4,
            "rating": 0.1,
            "relevance": 0.1,
            "traffic": 0.0,
            "cost": 0.0,
            "popularity": 0.0,
            "open_now": 0.0
        }

    # BEST → prioritize rating + popularity
    if "best" in q:
        return {
            "speed": 0.2,
            "distance": 0.1,
            "rating": 0.4,
            "relevance": 0.2,
            "traffic": 0.0,
            "cost": 0.0,
            "popularity": 0.3,
            "open_now": 0.0
        }

    # CHEAP / BUDGET
    if "cheap" in q or "budget" in q:
        return {
            "speed": 0.2,
            "distance": 0.2,
            "rating": 0.2,
            "relevance": 0.1,
            "traffic": 0.0,
            "cost": 0.3,
            "popularity": 0.0,
            "open_now": 0.0
        }

    # OPEN NOW
    if "open now" in q:
        return {
            "speed": 0.3,
            "distance": 0.2,
            "rating": 0.1,
            "relevance": 0.1,
            "traffic": 0.0,
            "cost": 0.0,
            "popularity": 0.0,
            "open_now": 0.3
        }

    # DEFAULT (balanced)
    return {
        "speed": 0.25,
        "distance": 0.25,
        "rating": 0.2,
        "relevance": 0.1,
        "traffic": 0.1,
        "cost": 0.05,
        "popularity": 0.05,
        "open_now": 0.0
    }


def compute_score(place, query):
    """
    Computes final score for a place using dynamic weights
    """

    weights = get_weights(query)

    # -------- EXISTING FEATURES --------
    distance = place.get("distance", 5)
    travel_time = place.get("travel_time", 10)
    rating = place.get("rating", 3.5)
    traffic = place.get("traffic_delay", 0)

    # -------- NEW FEATURES --------
    cost = place.get("cost", 2)                 # lower is better
    popularity = place.get("popularity", 0.5)   # 0–1 normalized
    open_now = place.get("open_now", True)

    # -------- NORMALIZATION --------
    proximity = 1 / (1 + distance)
    speed = 1 / (1 + travel_time)
    rating_norm = rating / 5.0
    cost_score = 1 / (1 + cost)
    open_score = 1.0 if open_now else 0.0

    # -------- RELEVANCE --------
    name = place.get("name", "").lower()
    relevance = 1 if any(word in name for word in query.lower().split()) else 0.5

    # -------- TRAFFIC --------
    traffic_penalty = -traffic

    # -------- FINAL SCORE --------
    score = (
        weights.get("speed", 0) * speed +
        weights.get("distance", 0) * proximity +
        weights.get("rating", 0) * rating_norm +
        weights.get("relevance", 0) * relevance +
        weights.get("traffic", 0) * traffic_penalty +

        # NEW COMPONENTS
        weights.get("cost", 0) * cost_score +
        weights.get("popularity", 0) * popularity +
        weights.get("open_now", 0) * open_score
    )

    return score


def rank_places(places, query):
    """
    Rank all places based on computed score
    """

    for p in places:
        p["score"] = compute_score(p, query)

    return sorted(places, key=lambda x: x["score"], reverse=True)