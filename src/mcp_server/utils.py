def latlng_to_lnglat(coord: str) -> str:
    """
    Convert 'lat,lng' -> 'lng,lat'
    Example: '28.3670,75.5880' -> '75.5880,28.3670'
    """
    parts = [x.strip() for x in coord.split(",")]
    if len(parts) != 2:
        raise ValueError(f"Invalid coordinate format: {coord}")

    lat, lng = parts
    return f"{lng},{lat}"

def latlng_list_to_lnglat_list(coords: list[str]) -> list[str]:
    return [latlng_to_lnglat(c) for c in coords]