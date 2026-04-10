from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import re


app = FastAPI(title="Dummy Agentic Map Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------
# Request Schemas
# ----------------------------

class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    input_mode: Optional[str] = "text"


class RouteRequest(BaseModel):
    origin: Dict[str, Any]
    destination: Dict[str, Any]


# ----------------------------
# Dummy Data
# ----------------------------

DUMMY_CENTER = {
    "lat": 28.3639,
    "lng": 75.5860
}

DUMMY_PLACES = [
    {
        "id": "place_1",
        "rank": 1,
        "name": "Cafe Mocha Pilani",
        "lat": 28.3648,
        "lng": 75.5871,
        "rating": 4.6,
        "distance_km": 0.7,
        "address": "Pilani Main Road",
        "category": "cafe",
        "open_now": True
    },
    {
        "id": "place_2",
        "rank": 2,
        "name": "Heritage Bites",
        "lat": 28.3660,
        "lng": 75.5890,
        "rating": 4.4,
        "distance_km": 1.0,
        "address": "Near Clock Tower",
        "category": "restaurant",
        "open_now": True
    },
    {
        "id": "place_3",
        "rank": 3,
        "name": "Green Leaf Veg Cafe",
        "lat": 28.3625,
        "lng": 75.5838,
        "rating": 4.5,
        "distance_km": 0.5,
        "address": "BITS Gate Market",
        "category": "cafe",
        "open_now": False
    },
    {
        "id": "place_4",
        "rank": 4,
        "name": "Railway View Snacks",
        "lat": 28.3692,
        "lng": 75.5924,
        "rating": 4.2,
        "distance_km": 1.6,
        "address": "Station Road",
        "category": "snacks",
        "open_now": True
    },
    {
        "id": "place_5",
        "rank": 5,
        "name": "Spice Route Diner",
        "lat": 28.3614,
        "lng": 75.5809,
        "rating": 4.3,
        "distance_km": 0.9,
        "address": "Hospital Chowk",
        "category": "restaurant",
        "open_now": True
    }
]


# ----------------------------
# Helpers
# ----------------------------

RANK_WORDS = {
    "first": 1,
    "1st": 1,
    "one": 1,
    "second": 2,
    "2nd": 2,
    "two": 2,
    "third": 3,
    "3rd": 3,
    "three": 3,
    "fourth": 4,
    "4th": 4,
    "four": 4,
    "fifth": 5,
    "5th": 5,
    "five": 5,
}


def detect_rank_reference(query: str) -> Optional[int]:
    q = query.lower().strip()

    for word, rank in RANK_WORDS.items():
        if re.search(rf"\b{re.escape(word)}\b", q):
            return rank

    digit_match = re.search(r"\b(\d+)\b", q)
    if digit_match:
        value = int(digit_match.group(1))
        if 1 <= value <= 10:
            return value

    return None


def is_focus_command(query: str) -> bool:
    q = query.lower()
    triggers = [
        "take me to",
        "go to",
        "focus on",
        "show me",
        "open the",
        "select",
        "third one",
        "first one",
        "second one"
    ]
    return any(t in q for t in triggers)


def summarize_places(places: List[Dict[str, Any]]) -> str:
    if not places:
        return "No results found."

    top = places[0]
    return (
        f"Found {len(places)} places. "
        f"Top result is {top['name']} "
        f"with rating {top.get('rating', 'N/A')} and distance "
        f"{top.get('distance_km', 'N/A')} kilometers."
    )


# ----------------------------
# Routes
# ----------------------------

@app.get("/")
def root():
    return {"status": "ok", "message": "Dummy backend is running."}


@app.post("/chat")
def chat(req: ChatRequest):
    query = req.query.strip()

    # Voice follow-up like: "take me to the third one"
    if is_focus_command(query):
        rank = detect_rank_reference(query)
        if rank is not None:
            selected = next((p for p in DUMMY_PLACES if p["rank"] == rank), None)
            if selected:
                return {
                    "action": "FOCUS_PLACE",
                    "place": selected,
                    "summary": f"Focusing on {selected['name']}, which is result number {rank}.",
                    "context": {
                        "session_id": req.session_id,
                        "previous_query": "dummy_previous_query"
                    }
                }

    # Normal search response
    return {
        "query": query,
        "center": DUMMY_CENTER,
        "places": DUMMY_PLACES,
        "summary": summarize_places(DUMMY_PLACES),
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
            "session_id": req.session_id,
            "previous_query": None
        }
    }


@app.post("/route")
def route(req: RouteRequest):
    origin = req.origin
    destination = req.destination

    o_lat = float(origin["lat"])
    o_lng = float(origin["lng"])
    d_lat = float(destination["lat"])
    d_lng = float(destination["lng"])

    # Dummy path with one midpoint
    mid_lat = (o_lat + d_lat) / 2 + 0.0008
    mid_lng = (o_lng + d_lng) / 2 + 0.0008

    return {
        "route": [
            [o_lat, o_lng],
            [mid_lat, mid_lng],
            [d_lat, d_lng]
        ],
        "eta": "8 mins",
        "distance_text": "1.4 km"
    }