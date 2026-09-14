from math import atan2, cos, radians, sin, sqrt


def haversine_miles(
    point_a: list[float],
    point_b: list[float],
) -> float:
    """
    GeoJSON points are [longitude, latitude].
    """

    lon1, lat1 = point_a
    lon2, lat2 = point_b

    earth_radius_miles = 3958.8

    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)

    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1_rad)
        * cos(lat2_rad)
        * sin(delta_lon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a),
    )

    return earth_radius_miles * c


def coordinate_at_fraction(
    coordinates: list[list[float]],
    fraction: float,
) -> dict:
    """
    Find an approximate coordinate along the route geometry.

    fraction:
        0.0 = beginning of route
        1.0 = end of route
    """

    if not coordinates:
        raise ValueError(
            "Route geometry contains no coordinates."
        )

    if len(coordinates) == 1:
        lon, lat = coordinates[0]

        return {
            "lat": lat,
            "lon": lon,
        }

    fraction = max(
        0.0,
        min(1.0, fraction),
    )

    segment_lengths = []
    total_length = 0.0

    for index in range(
        len(coordinates) - 1
    ):
        length = haversine_miles(
            coordinates[index],
            coordinates[index + 1],
        )

        segment_lengths.append(length)
        total_length += length

    if total_length <= 0:
        lon, lat = coordinates[0]

        return {
            "lat": lat,
            "lon": lon,
        }

    target_distance = (
        total_length * fraction
    )

    travelled = 0.0

    for index, segment_length in enumerate(
        segment_lengths
    ):
        next_travelled = (
            travelled + segment_length
        )

        if target_distance <= next_travelled:
            if segment_length <= 0:
                lon, lat = coordinates[index]

                return {
                    "lat": lat,
                    "lon": lon,
                }

            remaining = (
                target_distance - travelled
            )

            segment_fraction = (
                remaining / segment_length
            )

            start_lon, start_lat = (
                coordinates[index]
            )

            end_lon, end_lat = (
                coordinates[index + 1]
            )

            lon = (
                start_lon
                + (
                    end_lon - start_lon
                )
                * segment_fraction
            )

            lat = (
                start_lat
                + (
                    end_lat - start_lat
                )
                * segment_fraction
            )

            return {
                "lat": lat,
                "lon": lon,
            }

        travelled = next_travelled

    lon, lat = coordinates[-1]

    return {
        "lat": lat,
        "lon": lon,
    }

def build_route_stops(
    events: list[dict],
    route: dict,
    pickup_location: dict,
    dropoff_location: dict,
) -> list[dict]:

    route_distance = float(
        route["distance_miles"]
    )

    coordinates = (
        route["geometry"]["coordinates"]
    )

    cumulative_miles = 0.0
    stops = []

    for event in events:
        if event["status"] == "D":
            cumulative_miles += float(
                event.get("miles", 0)
            )

            continue

        reason = event["reason"]

        if reason == "Off duty":
            continue

        # Pickup and dropoff already have exact
        # geocoded coordinates.
        if reason == "Pickup":
            position = {
                "lat": pickup_location["lat"],
                "lon": pickup_location["lon"],
            }

        elif reason == "Dropoff":
            position = {
                "lat": dropoff_location["lat"],
                "lon": dropoff_location["lon"],
            }

        else:
            fraction = (
                cumulative_miles
                / route_distance
                if route_distance > 0
                else 0
            )

            position = coordinate_at_fraction(
                coordinates,
                fraction,
            )

        stops.append({
            "type": _stop_type(reason),
            "reason": reason,
            "status": event["status"],
            "start": event["start"],
            "end": event["end"],
            "duration_minutes":
                event["duration_minutes"],
            "route_mile": round(
                cumulative_miles,
                2,
            ),
            "lat": round(
                position["lat"],
                6,
            ),
            "lon": round(
                position["lon"],
                6,
            ),
        })

    return stops


def _stop_type(
    reason: str,
) -> str:

    if reason == "Pickup":
        return "pickup"

    if reason == "Dropoff":
        return "dropoff"

    if reason == "Fuel stop":
        return "fuel"

    if "34-hour" in reason:
        return "restart"

    if "10-hour" in reason:
        return "rest"

    if "30-minute" in reason:
        return "break"

    return "stop"