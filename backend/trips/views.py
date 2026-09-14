from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import TripPlanRequestSerializer
from .services.geocoding import (
    GeocodingError,
    geocode_location,
)
from .services.routing import (
    RoutingError,
    get_route,
)
import requests
from datetime import datetime
from .services.trip_planner import build_trip_plan


class TripPlanView(APIView):

    def post(self, request):
        serializer = TripPlanRequestSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        data = serializer.validated_data

        try:
            current = geocode_location(
                data["current_location"]
            )

            pickup = geocode_location(
                data["pickup_location"]
            )

            dropoff = geocode_location(
                data["dropoff_location"]
            )

            route = get_route(
                current=current,
                pickup=pickup,
                dropoff=dropoff,
            )

            trip_plan = build_trip_plan(
                route=route,
                current_location=current,
                pickup_location=pickup,
                dropoff_location=dropoff,
                current_cycle_used_hours=
                    data["current_cycle_used"],
                start_time=datetime.now().replace(
                            second=0,
                            microsecond=0,
                        ),
            )

        except (
            GeocodingError,
            RoutingError,
            requests.RequestException,
        ) as exc:
            return Response(
                {
                    "error": str(exc)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({
            "locations": {
                "current": current,
                "pickup": pickup,
                "dropoff": dropoff,
            },
            "route": route,
            "trip_plan": trip_plan,
        })