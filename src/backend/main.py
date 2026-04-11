from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Optional

from src.backend.memory.session_store import get_session, update_session
from src.backend.services.intent_parser import parse_intent
from src.backend.clients.mcp_client import MCPClient
from src.backend.services.ranking_service import rank_places
from src.backend.services.formatter import format_response
from src.backend.services.place_normalizer import normalize_places
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mcp_client = MCPClient()


class QueryRequest(BaseModel):
    query: str
    session_id: str
    user_location: Optional[dict[str, float]] = None
    map_center: Optional[dict[str, float]] = None
    selected_place_id: Optional[str] = None


def apply_dynamic_filters(places: list[dict[str, Any]], filters: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Generic deterministic filter application based on structured LLM output.
    """
    if not filters:
        return places

    def check(place: dict[str, Any], key: str, value: Any) -> bool:
        if key == "min_rating":
            return (place.get("rating") or 0) >= value

        if key == "max_distance":
            distance_value = place.get("matrix_distance")
            if distance_value is None:
                distance_value = place.get("distance", float("inf"))
            return distance_value <= value

        if key == "max_cost":
            return (place.get("cost") if place.get("cost") is not None else float("inf")) <= value

        if key == "min_popularity":
            return (place.get("popularity") or 0) >= value

        if key == "keyword":
            keyword = str(value).lower().strip()
            name = place.get("name", "").lower()
            address = place.get("address", "").lower()
            category = str(place.get("category", "")).lower()
            return keyword in name or keyword in address or keyword in category

        if key == "open_now":
            return place.get("open_now", False) == value

        if key == "veg_only":
            text_blob = " ".join(
                [
                    str(place.get("name", "")),
                    str(place.get("address", "")),
                    str(place.get("category", "")),
                ]
            ).lower()
            veg_markers = ["veg", "vegetarian", "pure veg"]
            return any(marker in text_blob for marker in veg_markers) if value else True

        if key == "parking":
            return place.get("parking", False) == value

        return True

    filtered = []
    for place in places:
        if all(check(place, k, v) for k, v in filters.items()):
            filtered.append(place)

    return filtered


def determine_search_radius(query: str, intent: dict[str, Any]) -> int:
    q = query.lower()

    if any(x in q for x in ["walkable", "near me", "nearby"]):
        return 1000
    if any(x in q for x in ["nearest", "closest"]):
        return 2000
    if any(x in q for x in ["station", "airport", "railway station"]):
        return 3000
    if any(x in q for x in ["best", "top", "popular", "famous"]):
        return 5000

    return 3000


def determine_search_strategy(query: str, intent: dict[str, Any]) -> str:
    """
    Decide whether to use nearby, text search, or hybrid retrieval.
    """
    q = query.lower()
    category = intent.get("category")
    location = intent.get("location")

    named_or_broad_search_signals = [
        "best",
        "top",
        "famous",
        "heritage",
        "tourist",
        "places to visit",
        "apollo",
        "ccd",
        "starbucks",
        "dominos",
        "pizza hut",
    ]

    if any(signal in q for signal in named_or_broad_search_signals):
        return "text_search"

    if category and location:
        return "nearby"

    return "hybrid"


def extract_center_from_geocode(geo_resp: dict[str, Any]) -> dict[str, Any]:
    """
    Safely extract lat/lng from various possible geocode response shapes.
    """
    candidates = geo_resp.get("results") or geo_resp.get("copResults") or []

    if not candidates:
        raise HTTPException(status_code=404, detail="Could not resolve location")

    first = candidates[0]

    lat = first.get("lat", first.get("latitude"))
    lng = first.get("lng", first.get("longitude"))

    if lat is None or lng is None:
        raise HTTPException(status_code=404, detail="Geocode response missing coordinates")

    return {"lat": float(lat), "lng": float(lng)}


def merge_candidate_results(
    nearby_places: list[dict[str, Any]],
    text_places: list[dict[str, Any]],
    top_k: int = 20,
) -> list[dict[str, Any]]:
    """
    Merge and de-duplicate results from multiple retrieval strategies.
    """
    merged = []
    seen = set()

    for place in nearby_places + text_places:
        key = (
            str(place.get("id", "")).strip().lower(),
            str(place.get("name", "")).strip().lower(),
            str(place.get("address", "")).strip().lower(),
        )
        if key in seen:
            continue
        seen.add(key)
        merged.append(place)

    return merged[:top_k]


def enrich_places_with_route_and_traffic(
    origin_lat: float,
    origin_lng: float,
    places: list[dict[str, Any]],
    max_candidates: int = 10,
) -> list[dict[str, Any]]:
    """
    Enrich shortlisted places with:
    - route distance
    - travel time
    - traffic delay

    This is still a fallback design.
    Later this should be replaced by Distance Matrix enrichment.
    """
    enriched = []
    shortlisted = places[:max_candidates]

    origin = f"{origin_lat},{origin_lng}"

    for place in shortlisted:
        lat = place.get("lat")
        lng = place.get("lng")

        if lat is None or lng is None:
            enriched.append(place)
            continue

        updated_place = dict(place)
        destination = f"{lat},{lng}"

        try:
            route_resp = mcp_client.route(origin, destination)

            if "distance" in route_resp:
                updated_place["distance"] = route_resp["distance"]

            if "duration" in route_resp:
                updated_place["travel_time"] = route_resp["duration"]

            if "routes" in route_resp and route_resp["routes"]:
                first_route = route_resp["routes"][0]
                if "distance" in first_route:
                    updated_place["distance"] = first_route["distance"]
                if "duration" in first_route:
                    updated_place["travel_time"] = first_route["duration"]

        except Exception:
            pass

        try:
            traffic_resp = mcp_client.traffic(destination)

            if "traffic_delay" in traffic_resp:
                updated_place["traffic_delay"] = traffic_resp["traffic_delay"]
            elif "delay" in traffic_resp:
                updated_place["traffic_delay"] = traffic_resp["delay"]

        except Exception:
            pass

        enriched.append(updated_place)

    if len(places) > max_candidates:
        enriched.extend(places[max_candidates:])

    return enriched


def process_query(query: str, session_id: str):
    # Step 0: Load session
    session = get_session(session_id)
    previous_query = session.get("last_query_text")

    # Step 1: Parse intent using LLM
    try:
        intent = parse_intent(query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intent parsing failed: {str(e)}")

    intent_type = intent.get("intent")

    # -----------------------------------
    # CASE 1: NEW SEARCH
    # -----------------------------------
    if intent_type == "search_places":
        location = intent.get("location", "current_location")
        category = intent.get("category", "place")
        filters = intent.get("filters", {})
        top_k = intent.get("top_k", 10)

        try:
            geo_resp = mcp_client.geocode(location)
            center = extract_center_from_geocode(geo_resp)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Geocoding failed: {str(e)}")

        lat = center["lat"]
        lng = center["lng"]

        search_strategy = determine_search_strategy(query, intent)
        radius = determine_search_radius(query, intent)

        raw_nearby = []
        raw_text = []

        try:
            if search_strategy == "nearby":
                nearby_resp = mcp_client.nearby(lat, lng, category, radius=radius)
                raw_nearby = nearby_resp.get("results", []) or nearby_resp.get("suggestedLocations", []) or []

            elif search_strategy == "text_search":
                text_resp = mcp_client.text_search(query=query, location=location, top_k=max(2 * top_k, 10))
                raw_text = text_resp.get("results", []) or []

            else:
                nearby_resp = mcp_client.nearby(lat, lng, category, radius=radius)
                raw_nearby = nearby_resp.get("results", []) or nearby_resp.get("suggestedLocations", []) or []

                text_resp = mcp_client.text_search(query=query, location=location, top_k=max(2 * top_k, 10))
                raw_text = text_resp.get("results", []) or []

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Place retrieval failed: {str(e)}")

        try:
            normalized_nearby = normalize_places(raw_nearby) if raw_nearby else []
            normalized_text = normalize_places(raw_text) if raw_text else []
            raw_places = merge_candidate_results(normalized_nearby, normalized_text, top_k=max(2 * top_k, 20))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Normalization failed: {str(e)}")

        filtered_places = apply_dynamic_filters(raw_places, filters)

        if not filtered_places and search_strategy == "nearby":
            try:
                broader_resp = mcp_client.nearby(lat, lng, category, radius=max(radius * 2, 5000))
                broader_raw = broader_resp.get("results", []) or broader_resp.get("suggestedLocations", []) or []
                broader_places = normalize_places(broader_raw)
                filtered_places = apply_dynamic_filters(broader_places, filters)
            except Exception:
                filtered_places = []

        enriched_places = enrich_places_with_route_and_traffic(lat, lng, filtered_places, max_candidates=10)

        ranked_places = rank_places(enriched_places, query)
        final_results = ranked_places[:top_k]

        update_session(
            session_id,
            {
                "last_results": final_results,
                "last_query": intent,
                "last_query_text": query,
                "center": {"lat": lat, "lng": lng},
                "last_radius": radius,
                "search_strategy": search_strategy,
                "used_traffic_matrix": False,
            },
        )

        return format_response(
            query,
            {"lat": lat, "lng": lng},
            final_results,
            session_id=session_id,
            previous_query=previous_query,
        )

    # -----------------------------------
    # CASE 2: FOLLOW-UP / REFINE
    # -----------------------------------
    if intent_type == "refine_results":
        previous_results = session.get("last_results", [])
        center = session.get("center")

        if not previous_results:
            return {"error": "No previous results to refine"}

        filters = intent.get("filters", {})
        filtered = apply_dynamic_filters(previous_results, filters)

        ranked_filtered = rank_places(filtered, query)

        update_session(
            session_id,
            {
                **session,
                "last_results": ranked_filtered,
                "last_query": intent,
                "last_query_text": query,
            },
        )

        return format_response(
            query,
            center,
            ranked_filtered,
            session_id=session_id,
            previous_query=previous_query,
        )

    return {"error": "Unsupported query"}


@app.get("/health")
def health():
    return {"status": "ok", "message": "Backend is running"}


@app.get("/query")
def handle_query_get(q: str, session_id: str):
    return process_query(q, session_id)


@app.post("/query")
def handle_query_post(req: QueryRequest):
    return process_query(req.query, req.session_id)