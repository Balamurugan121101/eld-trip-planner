import {
  MapContainer,
  Marker,
  Polyline,
  Popup,
  TileLayer,
  useMap,
} from "react-leaflet";

import L from "leaflet";
import { useEffect } from "react";

import type { TripResponse } from "../types/trip";

import "leaflet/dist/leaflet.css";


// Fix default Leaflet icons
delete (L.Icon.Default.prototype as any)._getIconUrl;

L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png",

  iconUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png",

  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
});


interface Props {
  trip: TripResponse;
}


// -------------------------------------
// Custom marker creator
// -------------------------------------

function createMarkerIcon(
  symbol: string,
  background: string,
  size = 38
) {
  return L.divIcon({
    className: "custom-map-marker",

    html: `
      <div
        style="
          width: ${size}px;
          height: ${size}px;
          background: ${background};
          border: 3px solid white;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 18px;
          box-shadow: 0 3px 10px rgba(0,0,0,0.30);
        "
      >
        ${symbol}
      </div>
    `,

    iconSize: [size, size],

    iconAnchor: [
      size / 2,
      size / 2,
    ],

    popupAnchor: [
      0,
      -(size / 2),
    ],
  });
}


// -------------------------------------
// Main route markers
// -------------------------------------

const currentIcon =
  createMarkerIcon(
    "●",
    "#2563eb",
    42
  );

const pickupIcon =
  createMarkerIcon(
    "P",
    "#16a34a",
    42
  );

const dropoffIcon =
  createMarkerIcon(
    "D",
    "#dc2626",
    42
  );


// -------------------------------------
// HOS stop markers
// -------------------------------------

const fuelIcon =
  createMarkerIcon(
    "⛽",
    "#ea580c"
  );

const breakIcon =
  createMarkerIcon(
    "☕",
    "#0891b2"
  );

const restIcon =
  createMarkerIcon(
    "🛏",
    "#7c3aed"
  );

const restartIcon =
  createMarkerIcon(
    "↻",
    "#be123c"
  );


function getStopIcon(
  type: string
) {
  switch (type) {
    case "fuel":
      return fuelIcon;

    case "break":
      return breakIcon;

    case "rest":
      return restIcon;

    case "restart":
      return restartIcon;

    default:
      return breakIcon;
  }
}


function getStopLabel(
  type: string
) {
  switch (type) {
    case "fuel":
      return "Fuel Stop";

    case "break":
      return "HOS Break";

    case "rest":
      return "10-Hour Rest";

    case "restart":
      return "34-Hour Restart";

    default:
      return "Stop";
  }
}


// -------------------------------------
// Fit map to route
// -------------------------------------

function FitBounds({
  positions,
}: {
  positions: [number, number][];
}) {
  const map = useMap();

  useEffect(() => {
    if (!positions.length) {
      return;
    }

    map.fitBounds(
      positions,
      {
        padding: [40, 40],
      }
    );
  }, [map, positions]);

  return null;
}


// -------------------------------------
// Component
// -------------------------------------

export default function TripMap({
  trip,
}: Props) {
  const routePositions:
    [number, number][] =
    trip.route.geometry.coordinates.map(
      ([lon, lat]) => [
        lat,
        lon,
      ]
    );


  const current:
    [number, number] = [
      trip.locations.current.lat,
      trip.locations.current.lon,
    ];


  const pickup:
    [number, number] = [
      trip.locations.pickup.lat,
      trip.locations.pickup.lon,
    ];


  const dropoff:
    [number, number] = [
      trip.locations.dropoff.lat,
      trip.locations.dropoff.lon,
    ];


  const boundsPositions = [
    ...routePositions,
    current,
    pickup,
    dropoff,
  ];


  return (
    <div className="map-wrapper">

      <MapContainer
        center={current}
        zoom={5}
        scrollWheelZoom
        className="trip-map"
      >

        <TileLayer
          attribution="&copy; OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />


        <Polyline
          positions={routePositions}
          pathOptions={{
            weight: 5,
            color: "#2563eb",
          }}
        />


        {/* Current location */}

        <Marker
          position={current}
          icon={currentIcon}
        >
          <Popup>

            <strong>
              Current Location
            </strong>

            <br />

            {
              trip.locations
                .current
                .display_name
            }

          </Popup>
        </Marker>


        {/* Pickup */}

        <Marker
          position={pickup}
          icon={pickupIcon}
        >
          <Popup>

            <strong>
              Pickup
            </strong>

            <br />

            {
              trip.locations
                .pickup
                .display_name
            }

          </Popup>
        </Marker>


        {/* Dropoff */}

        <Marker
          position={dropoff}
          icon={dropoffIcon}
        >
          <Popup>

            <strong>
              Dropoff
            </strong>

            <br />

            {
              trip.locations
                .dropoff
                .display_name
            }

          </Popup>
        </Marker>


        {/* HOS / Fuel stops */}

        {trip.trip_plan
          .route_stops
          .filter(
            (stop) =>
              stop.type !== "pickup" &&
              stop.type !== "dropoff"
          )
          .map(
            (
              stop,
              index
            ) => (

              <Marker
                key={
                  `${stop.type}-${index}`
                }

                position={[
                  stop.lat,
                  stop.lon,
                ]}

                icon={
                  getStopIcon(
                    stop.type
                  )
                }
              >

                <Popup>

                  <strong>
                    {
                      getStopLabel(
                        stop.type
                      )
                    }
                  </strong>

                  <br />

                  {stop.reason}

                  <br />

                  Route mile:{" "}
                  {
                    stop.route_mile
                      .toFixed(0)
                  }

                  <br />

                  Duration:{" "}
                  {
                    stop.duration_minutes
                  }{" "}
                  min

                  <br />

                  {new Date(
                    stop.start
                  ).toLocaleString()}

                </Popup>

              </Marker>
            )
          )}


        <FitBounds
          positions={
            boundsPositions
          }
        />

      </MapContainer>

    </div>
  );
}