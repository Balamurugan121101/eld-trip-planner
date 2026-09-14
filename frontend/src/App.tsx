import { useState } from "react";

import TripForm from "./components/TripForm";

import {
  planTrip,
  type TripRequest,
} from "./services/api";

import type {
  TripResponse,
} from "./types/trip";

import "./App.css";
import TripMap from "./components/TripMap";
import EldLogSheet from "./components/EldLogSheet";
import RouteInstructions from "./components/RouteInstructions";


function App() {
  const [trip, setTrip] =
    useState<TripResponse | null>(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);


  async function handlePlanTrip(
    request: TripRequest
  ) {
    try {
      setLoading(true);
      setError(null);

      const result =
        await planTrip(request);

      setTrip(result);

    } catch (err) {
      console.error(err);

      setError(
        "Unable to calculate trip. Please check the locations and try again."
      );

    } finally {
      setLoading(false);
    }
  }


  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>DriveLedger</h1>

          <p>
            HOS-aware trip planning &
            ELD logs
          </p>
        </div>
      </header>


      <main className="layout">

        <aside className="sidebar">

          <TripForm
            onSubmit={handlePlanTrip}
            loading={loading}
          />

          {error && (
            <div className="error">
              {error}
            </div>
          )}

        </aside>


        <section className="content">

          {!trip && (
            <div className="empty-state">

              <h2>
                Plan a compliant trip
              </h2>

              <p>
                Enter your route details
                to calculate driving,
                rest, fuel and ELD logs.
              </p>

            </div>
          )}


          {trip && (
            <>
              <div className="panel map-panel">
                <div className="panel-heading">
                  <div>
                    <h2>Route Overview</h2>
                    <p>
                      Current location → Pickup → Dropoff
                    </p>
                  </div>

                  <span className="route-distance">
                    {trip.route.distance_miles.toFixed(0)} mi
                  </span>
                </div>

                <TripMap trip={trip} />
              </div>

              <div className="summary-grid">

                <SummaryCard
                  label="Distance"
                  value={`${trip.route.distance_miles.toFixed(
                    0
                  )} mi`}
                />

                <SummaryCard
                  label="Driving Time"
                  value={`${trip.route.driving_hours.toFixed(
                    1
                  )} hrs`}
                />

                <SummaryCard
                  label="Cycle Remaining"
                  value={`${trip.trip_plan.cycle.remaining_hours.toFixed(
                    1
                  )} hrs`}
                />

                <SummaryCard
                  label="Log Sheets"
                  value={`${trip.trip_plan.daily_logs.length}`}
                />

              </div>

              <RouteInstructions trip={trip} />


              <div className="panel">

                <h2>
                  Trip Schedule
                </h2>

                {trip.trip_plan.events.map(
                  (event, index) => (
                    <div
                      className="event-row"
                      key={index}
                    >
                      <div
                        className={`status-badge status-${event.status}`}
                      >
                        {event.status}
                      </div>

                      <div>
                        <strong>
                          {event.reason}
                        </strong>

                        <p>
                          {new Date(
                            event.start
                          ).toLocaleString()}
                          {" → "}
                          {new Date(
                            event.end
                          ).toLocaleString()}
                        </p>
                      </div>

                    </div>
                  )
                )}

              </div>
              <div className="eld-section">
                <div className="eld-section-title">

                  <h2>
                    Daily ELD Logs
                  </h2>

                  <p>
                    Generated from the planned
                    duty-status schedule.
                  </p>

                </div>


                {trip.trip_plan.daily_logs.map(
                  (log) => (
                    <EldLogSheet
                      key={log.date}
                      log={log}
                    />
                  )
                )}

              </div>
            </>
          )}

        </section>

      </main>
    </div>
  );
}


function SummaryCard({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="summary-card">

      <span>
        {label}
      </span>

      <strong>
        {value}
      </strong>

    </div>
  );
}


export default App;