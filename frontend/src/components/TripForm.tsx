import { useState } from "react";
import type { TripRequest } from "../services/api";

interface Props {
  onSubmit: (data: TripRequest) => Promise<void>;
  loading: boolean;
}

export default function TripForm({
  onSubmit,
  loading,
}: Props) {
  const [currentLocation, setCurrentLocation] =
    useState("");

  const [pickupLocation, setPickupLocation] =
    useState("");

  const [dropoffLocation, setDropoffLocation] =
    useState("");

  const [cycleUsed, setCycleUsed] =
    useState(0);

  async function handleSubmit(
    event: React.FormEvent
  ) {
    event.preventDefault();

    await onSubmit({
      current_location: currentLocation,
      pickup_location: pickupLocation,
      dropoff_location: dropoffLocation,
      current_cycle_used: cycleUsed,
    });
  }

  return (
    <form
      className="trip-form"
      onSubmit={handleSubmit}
    >
      <h2>Plan your trip</h2>

      <div className="form-field">
        <label>Current location</label>

        <input
          type="text"
          placeholder="New York, NY"
          value={currentLocation}
          onChange={(e) =>
            setCurrentLocation(e.target.value)
          }
          required
        />
      </div>

      <div className="form-field">
        <label>Pickup location</label>

        <input
          type="text"
          placeholder="Chicago, IL"
          value={pickupLocation}
          onChange={(e) =>
            setPickupLocation(e.target.value)
          }
          required
        />
      </div>

      <div className="form-field">
        <label>Dropoff location</label>

        <input
          type="text"
          placeholder="Los Angeles, CA"
          value={dropoffLocation}
          onChange={(e) =>
            setDropoffLocation(e.target.value)
          }
          required
        />
      </div>

      <div className="form-field">
        <label>
          Current Cycle Used (Hours)
        </label>

        <input
          type="number"
          min="0"
          max="70"
          step="0.5"
          value={cycleUsed}
          onChange={(e) =>
            setCycleUsed(
              Number(e.target.value)
            )
          }
          required
        />
      </div>

      <button
        type="submit"
        disabled={loading}
      >
        {loading
          ? "Planning..."
          : "Plan Trip"}
      </button>
    </form>
  );
}