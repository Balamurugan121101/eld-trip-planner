import requests


OSRM_URL = "https://router.project-osrm.org"


class RoutingError(Exception):
    pass


def get_route(
    current: dict,
    pickup: dict,
    dropoff: dict,
) -> dict:

    coordinates = ";".join([
        f"{current['lon']},{current['lat']}",
        f"{pickup['lon']},{pickup['lat']}",
        f"{dropoff['lon']},{dropoff['lat']}",
    ])

    url = (
        f"{OSRM_URL}/route/v1/driving/"
        f"{coordinates}"
    )

    params = {
        "overview": "full",
        "geometries": "geojson",
        "steps": "true",
    }

    response = requests.get(
        url,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    if data.get("code") != "Ok":
        raise RoutingError(
            data.get(
                "message",
                "Unable to calculate route",
            )
        )

    route = data["routes"][0]

    legs = []

    for index, leg in enumerate(route["legs"]):
        steps = []

        for step in leg["steps"]:
            maneuver = step.get("maneuver", {})

            steps.append({
                "instruction": _build_instruction(step),
                "distance_miles": round(
                    step["distance"] * 0.000621371,
                    2,
                ),
                "duration_minutes": round(
                    step["duration"] / 60,
                    1,
                ),
                "location": maneuver.get(
                    "location"
                ),
            })

        legs.append({
            "index": index,
            "distance_miles": round(
                leg["distance"] * 0.000621371,
                2,
            ),
            "duration_minutes": round(
                leg["duration"] / 60,
            ),
            "steps": steps,
        })

    return {
        "distance_miles": round(
            route["distance"] * 0.000621371,
            2,
        ),
        "driving_minutes": round(
            route["duration"] / 60
        ),
        "driving_hours": round(
            route["duration"] / 3600,
            2,
        ),
        "geometry": route["geometry"],
        "legs": legs,
    }


def _build_instruction(step: dict) -> str:
    maneuver = step.get("maneuver", {})

    maneuver_type = maneuver.get(
        "type",
        "continue",
    )

    modifier = maneuver.get(
        "modifier",
        "",
    )

    road = step.get("name") or "road"

    if maneuver_type == "depart":
        return f"Start on {road}"

    if maneuver_type == "arrive":
        return "Arrive at destination"

    if modifier:
        return (
            f"{maneuver_type.replace('_', ' ').title()} "
            f"{modifier} onto {road}"
        )

    return (
        f"{maneuver_type.replace('_', ' ').title()} "
        f"onto {road}"
    )