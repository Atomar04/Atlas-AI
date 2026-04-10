import math


def safe_float(value, default):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_bool(value, default=False):
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        v = value.strip().lower()
        if v in {"true", "yes", "open", "1"}:
            return True
        if v in {"false", "no", "closed", "0"}:
            return False

    return default


def derive_popularity(raw_place):
    """
    Normalize popularity to 0..1 if possible.
    Prefer review count / rating count / similar fields if present.
    """
    review_count = (
        raw_place.get("review_count")
        or raw_place.get("ratings_count")
        or raw_place.get("user_ratings_total")
        or 0
    )

    review_count = safe_float(review_count, 0)

    # Smooth bounded scaling into [0,1)
    # 0 reviews -> 0
    # large reviews -> approaches 1
    return review_count / (review_count + 100.0)


def derive_cost(raw_place):
    """
    Normalize cost to a small numeric scale where lower = cheaper.
    Default is mid-range = 2.
    """
    possible = (
        raw_place.get("cost")
        or raw_place.get("price_level")
        or raw_place.get("price")
        or raw_place.get("avg_cost")
    )

    if possible is None:
        return 2

    # If numeric already, use it
    if isinstance(possible, (int, float)):
        return float(possible)

    # If text, map roughly
    text = str(possible).strip().lower()

    if text in {"low", "cheap", "budget", "1"}:
        return 1.0
    if text in {"medium", "moderate", "mid", "2"}:
        return 2.0
    if text in {"high", "expensive", "premium", "3"}:
        return 3.0

    return 2.0


def derive_open_now(raw_place):
    """
    Conservative fallback:
    - use explicit status fields if available
    - otherwise default to False for filtering safety, or True for ranking softness
    Here we choose False for truth-sensitive filters.
    """
    return safe_bool(
        raw_place.get("open_now")
        or raw_place.get("is_open")
        or raw_place.get("currently_open"),
        default=False
    )


def normalize_place(raw_place):
    """
    Convert raw Mappls place object into a stable internal schema.
    """
    lat = safe_float(
        raw_place.get("lat") or raw_place.get("latitude"),
        0.0
    )
    lng = safe_float(
        raw_place.get("lng") or raw_place.get("lon") or raw_place.get("longitude"),
        0.0
    )

    rating = safe_float(raw_place.get("rating"), 3.5)
    distance = safe_float(raw_place.get("distance"), 5.0)
    travel_time = safe_float(raw_place.get("travel_time"), 10.0)
    traffic_delay = safe_float(raw_place.get("traffic_delay"), 0.0)

    normalized = {
        "id": raw_place.get("id") or raw_place.get("place_id") or raw_place.get("mapplsPin"),
        "name": raw_place.get("name") or raw_place.get("place_name") or "Unknown Place",
        "address": raw_place.get("address") or raw_place.get("place_address") or "",
        "category": raw_place.get("category") or raw_place.get("type") or "",
        "lat": lat,
        "lng": lng,

        # ranking/filtering fields
        "rating": rating,
        "distance": distance,
        "travel_time": travel_time,
        "traffic_delay": traffic_delay,
        "cost": derive_cost(raw_place),
        "popularity": derive_popularity(raw_place),
        "open_now": derive_open_now(raw_place),

        # keep raw for debugging / future use
        "raw": raw_place
    }

    return normalized


def normalize_places(raw_places):
    return [normalize_place(p) for p in raw_places]