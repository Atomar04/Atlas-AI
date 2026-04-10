import requests

MCP_BASE = "http://localhost:8000"


def geocode(location):
    return requests.post(f"{MCP_BASE}/tool/geocode", json={
        "address": location
    }).json()


def nearby(lat, lng, keyword):
    return requests.post(f"{MCP_BASE}/tool/nearby", json={
        "lat": lat,
        "lng": lng,
        "keyword": keyword
    }).json()


def get_route(start_lat, start_lng, end_lat, end_lng):
    return requests.post(f"{MCP_BASE}/tool/route", json={
        "start": f"{start_lat},{start_lng}",
        "end": f"{end_lat},{end_lng}"
    }).json()


def get_traffic(lat, lng):
    return requests.post(f"{MCP_BASE}/tool/traffic", json={
        "lat": lat,
        "lng": lng
    }).json()