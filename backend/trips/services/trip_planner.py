from datetime import datetime

from .hos import (
    HOSPlanner,
    PICKUP_DURATION,
    DROPOFF_DURATION,
)
from .daily_logs import build_daily_logs
from .route_positions import build_route_stops


def build_trip_plan(
    route: dict,
    current_location: dict,
    pickup_location: dict,
    dropoff_location: dict,
    current_cycle_used_hours: float,
    start_time: datetime,
):
    planner = HOSPlanner(
        start_time=start_time,
        current_cycle_used_hours=current_cycle_used_hours,
    )

    legs = route["legs"]

    if len(legs) < 2:
        raise ValueError(
            "Expected route to contain current→pickup "
            "and pickup→dropoff legs."
        )

    current_to_pickup = legs[0]
    pickup_to_dropoff = legs[1]

    # 1. Drive from current location to pickup
    planner.drive(
        total_minutes=current_to_pickup["duration_minutes"],
        total_miles=current_to_pickup["distance_miles"],
        location=pickup_location["display_name"],
    )

    # 2. Pickup activity - 1 hour on duty
    planner.add_on_duty_stop(
        minutes=PICKUP_DURATION,
        reason="Pickup",
        location=pickup_location["display_name"],
    )

    # If pickup consumed the remaining cycle,
    # restart before any further driving.
    planner.ensure_cycle_for_driving(
        pickup_location["display_name"]
    )

    # 3. Drive pickup → dropoff
    planner.drive(
        total_minutes=pickup_to_dropoff["duration_minutes"],
        total_miles=pickup_to_dropoff["distance_miles"],
        location=dropoff_location["display_name"],
    )

    # 4. Dropoff activity - 1 hour on duty
    planner.add_on_duty_stop(
        minutes=DROPOFF_DURATION,
        reason="Dropoff",
        location=dropoff_location["display_name"],
    )

    events = planner.get_events()

    daily_logs = build_daily_logs(
                    events
                )

    route_stops = build_route_stops(
                    events=events,
                    route=route,
                    pickup_location=pickup_location,
                    dropoff_location=dropoff_location,
                )

    return {
        "start_time": start_time.isoformat(),
        "end_time": planner.current_time.isoformat(),
        "events": events,
        "route_stops": route_stops,
        "daily_logs": daily_logs,
        "cycle": {
            "starting_used_hours":
                round(current_cycle_used_hours, 2),
            "ending_used_hours":
                round(planner.cycle_used / 60, 2),
            "remaining_hours":
                round(
                    max(
                        0,
                        (
                            70 * 60
                            - planner.cycle_used
                        ) / 60,
                    ),
                    2,
                ),
        },
    }