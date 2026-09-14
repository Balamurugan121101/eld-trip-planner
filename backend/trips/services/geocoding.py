import requests


NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


class GeocodingError(Exception):
    pass


def geocode_location(location: str) -> dict:
    params = {
        "q": location,
        "format": "jsonv2",
        "limit": 1,
        "countrycodes": "us",
    }

    headers = {
        "User-Agent": "eld-trip-planner-assessment/1.0"
    }

    response = requests.get(
        NOMINATIM_URL,
        params=params,
        headers=headers,
        timeout=20,
    )

    response.raise_for_status()

    results = response.json()

    if not results:
        raise GeocodingError(
            f"Unable to locate '{location}'"
        )

    result = results[0]

    return {
        "query": location,
        "display_name": result["display_name"],
        "lat": float(result["lat"]),
        "lon": float(result["lon"]),
    }