from fastapi import FastAPI
from pydantic import BaseModel

from src.mcp_server.tools.geocode import geocode_address
from src.mcp_server.tools.nearby import search_nearby
from src.mcp_server.tools.routing import get_route

app = FastAPI()

# -------- Request Schemas --------

class GeocodeRequest(BaseModel):
    address: str

class NearbyRequest(BaseModel):
    lat: float
    lng: float
    keyword: str

class RouteRequest(BaseModel):
    start: str
    end: str

# -------- MCP Tools --------

@app.post("/tool/geocode")
def geocode(req: GeocodeRequest):
    return geocode_address(req.address)

@app.post("/tool/nearby")
def nearby(req: NearbyRequest):
    return search_nearby(req.lat, req.lng, req.keyword)

@app.post("/tool/route")
def route(req: RouteRequest):
    return get_route(req.start, req.end)