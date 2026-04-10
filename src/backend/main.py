from fastapi import FastAPI

from src.backend.memory.session_store import get_session, update_session
from src.backend.services.intent_parser import parse_intent
from src.backend.clients.mcp_client import geocode, nearby, get_route, get_traffic
from src.backend.services.ranking_service import rank_places
from src.backend.services.formatter import format_response
from src.backend.services.place_normalizer import normalize_places

def apply_dynamic_filters(places, filters):
    """
    Generic filter application based on LLM output.
    The LLM decides which filters to produce.
    Backend applies them deterministically.
    """

    def check(place, key, value):
        if key == "min_rating":
            return place.get("rating", 0) >= value

        if key == "max_distance":
            return place.get("distance", float("inf")) <= value

        if key == "max_cost":
            return place.get("cost", float("inf")) <= value

        if key == "min_popularity":
            return place.get("popularity", 0) >= value

        if key == "keyword":
            return value.lower() in place.get("name", "").lower()

        if key == "open_now":
            return place.get("open_now", False) == value

        return True

    filtered = []

    for p in places:
        if all(check(p, k, v) for k, v in filters.items()):
            filtered.append(p)

    return filtered

def enrich_places_with_route_and_traffic(origin_lat, origin_lng, places, max_candidates=10):
    """
    Enrich shortlisted places with:
    - route distance
    - travel time
    - traffic delay

    Only enrich top-N candidates to avoid too many API calls.
    """

    enriched = []

    shortlisted = places[:max_candidates]

    for place in shortlisted:
        lat = place.get("lat")
        lng = place.get("lng")

        if lat is None or lng is None:
            enriched.append(place)
            continue

        updated_place = dict(place)

        # -------- Route enrichment --------
        try:
            route_resp = get_route(origin_lat, origin_lng, lat, lng)

            # Adjust these keys based on actual MCP output shape
            if "distance" in route_resp:
                updated_place["distance"] = route_resp["distance"]

            if "duration" in route_resp:
                updated_place["travel_time"] = route_resp["duration"]

            # Optional alternative keys if your MCP returns nested route data
            if "routes" in route_resp and route_resp["routes"]:
                first_route = route_resp["routes"][0]

                if "distance" in first_route:
                    updated_place["distance"] = first_route["distance"]

                if "duration" in first_route:
                    updated_place["travel_time"] = first_route["duration"]

        except Exception:
            pass

        # -------- Traffic enrichment --------
        try:
            traffic_resp = get_traffic(lat, lng)

            # Adjust key names according to actual MCP response
            if "traffic_delay" in traffic_resp:
                updated_place["traffic_delay"] = traffic_resp["traffic_delay"]
            elif "delay" in traffic_resp:
                updated_place["traffic_delay"] = traffic_resp["delay"]

        except Exception:
            pass

        enriched.append(updated_place)

    # keep any remaining places unchanged
    if len(places) > max_candidates:
        enriched.extend(places[max_candidates:])

    return enriched

app = FastAPI()

@app.get("/query")
def handle_query(q: str, session_id: str):
    
    # Step 0: Load session
    session = get_session(session_id)
    previous_query = session.get("last_query_text")
    
    # Step 1: Parse intent using LLM
    intent = parse_intent(q)

    # -------------------------------
    # CASE 1: NEW SEARCH
    # -------------------------------
    if intent["intent"] == "search_places":
        location = intent.get("location", "current_location")

        # Step 2: Resolve location
        geo = geocode(location)

        lat = geo["results"][0]["lat"]
        lng = geo["results"][0]["lng"]

        # Step 3: Fetch places
        places = nearby(lat, lng, intent["category"])
        raw_places = places.get("results", [])
        raw_places = normalize_places(raw_places)
        

        # Optional: apply initial filters from LLM even on first search
        filters = intent.get("filters", {})
        if filters:
            raw_places = apply_dynamic_filters(raw_places, filters)

        # Optional: apply initial filters from LLM even on first search
        filters = intent.get("filters", {})
        if filters:
            raw_places = apply_dynamic_filters(raw_places, filters)

        enriched_places = enrich_places_with_route_and_traffic(lat, lng, raw_places, max_candidates=10)

        # Step 4: Rank
        ranked = rank_places(enriched_places, q)

        top_k = intent.get("top_k", 10)
        final_results = ranked[:top_k]

        # SAVE SESSION
        update_session(session_id, {
            "last_results": final_results,
            "last_query": intent,
            "last_query_text": q,
            "center": {"lat": lat, "lng": lng}
        })

        # Step 5: Format response
        return format_response(q, {"lat": lat, "lng": lng}, final_results,
                            session_id=session_id,
                            previous_query=previous_query
                        )

    # -------------------------------
    # CASE 2: FOLLOW-UP / REFINE
    # -------------------------------
    elif intent["intent"] == "refine_results":
        previous_results = session.get("last_results", [])

        if not previous_results:
            return {"error": "No previous results to refine"}

        filters = intent.get("filters", {})
        filtered = apply_dynamic_filters(previous_results, filters)

        # Re-rank refined results for the new query
        ranked_filtered = rank_places(filtered, q)

        # UPDATE SESSION
        update_session(session_id, {
            **session,
            "last_results": ranked_filtered,
            "last_query": intent,
            "last_query_text": q
        })

        return format_response(
            q,
            session.get("center"),
            ranked_filtered,
            session_id=session_id,
            previous_query=previous_query
        )
    
    return {"error": "Unsupported query"}