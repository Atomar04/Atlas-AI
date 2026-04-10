def get_weights(query):
    """
    Returns dynamic weights based on query language.
    """
    q = query.lower()

    # NEAREST / CLOSEST
    if "nearest" in q or "closest" in q:
        return {
            "speed": 0.35,
            "distance": 0.40,
            "rating": 0.10,
            "relevance": 0.10,
            "traffic": 0.05,
            "cost": 0.0,
            "popularity": 0.0,
            "open_now": 0.0,
        }

    # BEST / TOP
    if "best" in q or "top" in q:
        return {
            "speed": 0.10,
            "distance": 0.10,
            "rating": 0.35,
            "relevance": 0.20,
            "traffic": 0.05,
            "cost": 0.0,
            "popularity": 0.20,
            "open_now": 0.0,
        }

    # CHEAP / BUDGET
    if "cheap" in q or "budget" in q or "affordable" in q:
        return {
            "speed": 0.15,
            "distance": 0.15,
            "rating": 0.15,
            "relevance": 0.10,
            "traffic": 0.05,
            "cost": 0.35,
            "popularity": 0.05,
            "open_now": 0.0,
        }

    # OPEN NOW
    if "open now" in q:
        return {
            "speed": 0.20,
            "distance": 0.15,
            "rating": 0.10,
            "relevance": 0.10,
            "traffic": 0.05,
            "cost": 0.0,
            "popularity": 0.0,
            "open_now": 0.40,
        }

    # DEFAULT
    return {
        "speed": 0.25,
        "distance": 0.20,
        "rating": 0.20,
        "relevance": 0.15,
        "traffic": 0.10,
        "cost": 0.05,
        "popularity": 0.05,
        "open_now": 0.0,
    }


def compute_relevance(place, query):
    query_words = [w.strip() for w in query.lower().split() if w.strip()]

    text = " ".join(
        [
            str(place.get("name", "")),
            str(place.get("address", "")),
            str(place.get("category", "")),
        ]
    ).lower()

    if not query_words:
        return 0.5

    matches = sum(1 for w in query_words if w in text)
    return matches / len(query_words)


def compute_score(place, query):
    """
    Computes final score for a place using dynamic weights.
    Prefers matrix fields when available.
    """
    weights = get_weights(query)

    distance = place.get("matrix_distance")
    if distance is None:
        distance = place.get("distance")
    if distance is None:
        distance = 5.0

    travel_time = place.get("matrix_eta")
    if travel_time is None:
        travel_time = place.get("travel_time")
    if travel_time is None:
        travel_time = 10.0

    rating = place.get("rating")
    if rating is None:
        rating = 3.5

    traffic = place.get("traffic_delay")
    if traffic is None:
        traffic = 0.0

    cost = place.get("cost")
    if cost is None:
        cost = 2.0

    popularity = place.get("popularity")
    if popularity is None:
        popularity = 0.0

    open_now = place.get("open_now", False)

    proximity = 1 / (1 + distance)
    speed = 1 / (1 + travel_time)
    rating_norm = rating / 5.0
    cost_score = 1 / (1 + cost)
    open_score = 1.0 if open_now else 0.0
    relevance = compute_relevance(place, query)

    # lower delay is better
    traffic_score = 1 / (1 + traffic)

    score = (
        weights.get("speed", 0) * speed
        + weights.get("distance", 0) * proximity
        + weights.get("rating", 0) * rating_norm
        + weights.get("relevance", 0) * relevance
        + weights.get("traffic", 0) * traffic_score
        + weights.get("cost", 0) * cost_score
        + weights.get("popularity", 0) * popularity
        + weights.get("open_now", 0) * open_score
    )

    return score


def rank_places(places, query):
    """
    Rank all places based on computed score.
    """
    ranked = []
    for place in places:
        p = dict(place)
        p["score"] = compute_score(p, query)
        ranked.append(p)

    return sorted(ranked, key=lambda x: x["score"], reverse=True)