def safe_float(value, default=None):
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
    Normalize popularity roughly to 0..1 using available count-like fields.
    """
    review_count = (
        raw_place.get("review_count")
        or raw_place.get("ratings_count")
        or raw_place.get("user_ratings_total")
        or raw_place.get("rating_count")
        or 0
    )

    review_count = safe_float(review_count, 0)
    return review_count / (review_count + 100.0)


def derive_cost(raw_place):
    """
    Normalize cost to a small numeric scale where lower = cheaper.
    """
    possible = (
        raw_place.get("cost")
        or raw_place.get("price_level")
        or raw_place.get("price")
        or raw_place.get("avg_cost")
    )

    if possible is None:
        return 2.0

    if isinstance(possible, (int, float)):
        return float(possible)

    text = str(possible).strip().lower()

    if text in {"low", "cheap", "budget", "1"}:
        return 1.0
    if text in {"medium", "moderate", "mid", "2"}:
        return 2.0
    if text in {"high", "expensive", "premium", "3"}:
        return 3.0

    return 2.0


def derive_open_now(raw_place):
    return safe_bool(
        raw_place.get("open_now")
        or raw_place.get("is_open")
        or raw_place.get("currently_open"),
        default=False,
    )


def derive_parking(raw_place):
    return safe_bool(
        raw_place.get("parking")
        or raw_place.get("has_parking")
        or raw_place.get("parking_available"),
        default=False,
    )


def normalize_place(raw_place):
    """
    Convert raw place object into a stable internal schema.
    Supports both nearby-style and text-search-style responses.
    """
    lat = safe_float(
        raw_place.get("lat")
        or raw_place.get("latitude"),
        None,
    )
    lng = safe_float(
        raw_place.get("lng")
        or raw_place.get("lon")
        or raw_place.get("longitude"),
        None,
    )

    normalized = {
        "id": raw_place.get("id")
              or raw_place.get("place_id")
              or raw_place.get("mapplsPin")
              or raw_place.get("eLoc"),

        "name": raw_place.get("name")
                or raw_place.get("place_name")
                or raw_place.get("placeName")
                or "Unknown Place",

        "address": raw_place.get("address")
                   or raw_place.get("place_address")
                   or raw_place.get("placeAddress")
                   or "",

        "category": raw_place.get("category")
                    or raw_place.get("type")
                    or raw_place.get("poiType")
                    or "",

        "lat": lat,
        "lng": lng,

        # current ranking/filter fields
        "rating": safe_float(raw_place.get("rating"), None),
        "distance": safe_float(raw_place.get("distance"), None),
        "travel_time": safe_float(raw_place.get("travel_time"), None),
        "traffic_delay": safe_float(raw_place.get("traffic_delay"), 0.0),

        "cost": derive_cost(raw_place),
        "popularity": derive_popularity(raw_place),
        "open_now": derive_open_now(raw_place),
        "parking": derive_parking(raw_place),

        # future enrichment fields
        "matrix_distance": safe_float(raw_place.get("matrix_distance"), None),
        "matrix_eta": safe_float(raw_place.get("matrix_eta"), None),

        # keep raw for debugging
        "raw": raw_place,
    }

    return normalized


def normalize_places(raw_places):
    return [normalize_place(p) for p in raw_places]