from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from src.mcp_server.tools.geocode import geocode_address
from src.mcp_server.tools.nearby import search_nearby
from src.mcp_server.tools.routing import get_route
from src.mcp_server.tools.traffic import get_traffic
from src.mcp_server.tools.place_details import get_place_details
from src.mcp_server.tools.text_search import text_search
from src.mcp_server.tools.distance_matrix import distance_matrix
from src.mcp_server.tools.distance_matrix_eta import distance_matrix_eta

app = FastAPI(title="Mappls MCP Server", version="2.0")


class GeocodeRequest(BaseModel):
    address: str


class NearbyRequest(BaseModel):
    lat: float
    lng: float
    keyword: str
    radius: int = 3000


class RouteRequest(BaseModel):
    origin: str
    destination: str


class TrafficRequest(BaseModel):
    route_id: str


class PlaceDetailsRequest(BaseModel):
    place_id: str


class TextSearchRequest(BaseModel):
    query: str
    location: Optional[str] = ""
    top_k: int = 10


class DistanceMatrixRequest(BaseModel):
    origin: str
    destinations: List[str]


@app.get("/")
def health():
    return {"status": "ok", "message": "MCP server running"}


@app.post("/tool/geocode")
def tool_geocode(req: GeocodeRequest):
    try:
        return geocode_address(req.address)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tool/nearby")
def tool_nearby(req: NearbyRequest):
    try:
        return search_nearby(req.lat, req.lng, req.keyword, req.radius)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tool/route")
def tool_route(req: RouteRequest):
    try:
        return get_route(req.origin, req.destination)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tool/traffic")
def tool_traffic(req: TrafficRequest):
    try:
        return get_traffic(req.route_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tool/place_details")
def tool_place_details(req: PlaceDetailsRequest):
    try:
        return get_place_details(req.place_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tool/text_search")
def tool_text_search(req: TextSearchRequest):
    try:
        return text_search(req.query, req.location, req.top_k)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tool/distance_matrix")
def tool_distance_matrix(req: DistanceMatrixRequest):
    try:
        return distance_matrix(req.origin, req.destinations)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tool/distance_matrix_eta")
def tool_distance_matrix_eta(req: DistanceMatrixRequest):
    try:
        return distance_matrix_eta(req.origin, req.destinations)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))