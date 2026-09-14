import type { TripResponse } from "../types/trip";

interface Props {
  trip: TripResponse;
}

export default function RouteInstructions({
  trip,
}: Props) {
  const legNames = [
    "Current Location → Pickup",
    "Pickup → Dropoff",
  ];

  return (
    <div className="panel route-instructions">
      <h2>Route Instructions</h2>

      {trip.route.legs.map((leg) => (
        <div
          className="route-leg"
          key={leg.index}
        >
          <div className="route-leg-header">
            <strong>
              {legNames[leg.index] ??
                `Route Leg ${leg.index + 1}`}
            </strong>

            <span>
              {leg.distance_miles.toFixed(0)} mi
              {" · "}
              {(leg.duration_minutes / 60).toFixed(1)} hrs
            </span>
          </div>

          <div className="route-steps">
            {leg.steps.map((step, index) => (
              <div
                className="route-step"
                key={index}
              >
                <span className="step-number">
                  {index + 1}
                </span>

                <div>
                  <strong>
                    {step.instruction}
                  </strong>

                  <p>
                    {step.distance_miles.toFixed(1)} mi
                    {" · "}
                    {step.duration_minutes.toFixed(0)} min
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}

      <p className="routing-note">
        Route guidance is based on OpenStreetMap/OSRM
        road routing and is not truck-specific navigation.
      </p>
    </div>
  );
}