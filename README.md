# DriveLedger – ELD Trip Planner

DriveLedger is a full-stack trip planning application for property-carrying commercial drivers. It generates a route from the driver's current location through pickup and dropoff locations, applies Hours of Service (HOS) constraints, schedules required rest/fuel stops, and produces daily ELD-style log sheets.

## Features

- Current, pickup, and dropoff location input
- Current 70-hour cycle usage input
- Route generation and map visualization
- Route distance and estimated driving time
- Pickup and dropoff stops
- 30-minute HOS breaks
- 10-hour daily rest periods
- 34-hour cycle restart when required
- Fuel stops at least every 1,000 miles
- Route instructions
- Trip duty-status timeline
- Multiple daily ELD-style log sheets for long trips
- Daily OFF / SB / D / ON duty totals
- Daily driving mileage
- Responsive React interface

## Tech Stack

### Backend

- Python
- Django
- Django REST Framework
- Requests
- Gunicorn

### Frontend

- React
- TypeScript
- Vite
- Axios
- React Leaflet
- Leaflet

### External Services

- OpenStreetMap / Nominatim – location geocoding
- OSRM – route calculation
- OpenStreetMap – map tiles

## HOS Rules Implemented

The planner models the assignment as a property-carrying driver operating under the 70-hour / 8-day cycle.

The planning engine implements:

- Maximum 11 hours of driving after 10 consecutive hours off duty
- 14-hour driving window
- 30-minute non-driving break after 8 cumulative hours of driving
- 70-hour / 8-day cycle limit
- 34 consecutive hours off duty for cycle restart
- Pickup time: 1 hour on duty
- Dropoff time: 1 hour on duty
- Fueling treated as on-duty, non-driving time
- Fuel stop scheduled no later than every 1,000 miles

Pickup, dropoff, and fueling count toward on-duty/cycle time.

## Assumptions

The assessment provides the driver's current cycle usage as one aggregate number rather than the driver's previous eight days of duty history.

Because the previous eight days are unavailable, the application cannot calculate exact rolling-hour recapture. The supplied cycle usage is therefore treated as already-consumed cycle time. If the remaining cycle time is exhausted and additional driving is required, the planner schedules a 34-hour restart.

Additional assumptions:

- Property-carrying driver
- 70-hour / 8-day cycle
- No adverse driving conditions
- Split sleeper-berth rules are outside the scope of this implementation
- Fuel stops are modeled as 30 minutes
- A qualifying 30-minute fuel stop can satisfy the required non-driving break
- All generated log times use one consistent planning/home-terminal time basis
- Pickup takes 1 hour
- Dropoff takes 1 hour

## Routing Limitation

OSRM and OpenStreetMap are used to provide free routing for this assessment.

The generated route is standard road routing and is **not truck-specific navigation**. It does not guarantee commercial-vehicle restrictions such as truck-only routing, vehicle height/weight restrictions, hazardous-material restrictions, or commercial road restrictions.

Rest and fuel markers are planned positions estimated along the generated route and are not recommendations for specific truck stops or facilities.

## ELD Logs

The application generates one ELD-style log sheet for every calendar day covered by the trip.

Each log contains the four standard duty-status categories:

- OFF – Off Duty
- SB – Sleeper Berth
- D – Driving
- ON – On Duty (Not Driving)

Events crossing midnight are split between the corresponding daily logs. Driving mileage is distributed proportionally between the split events.

Unused portions of each day are represented as off-duty time so that each daily log represents a complete 24-hour period.

> The generated logs are intended as a trip-planning demonstration and are not a certified Electronic Logging Device (ELD).

## Project Structure

```text
eld-trip-planner/
│
├── backend/
│   ├── config/
│   ├── trips/
│   │   ├── services/
│   │   │   ├── geocoding.py
│   │   │   ├── routing.py
│   │   │   ├── hos.py
│   │   │   ├── trip_planner.py
│   │   │   ├── daily_logs.py
│   │   │   └── route_positions.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   └── manage.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── TripForm.tsx
│   │   │   ├── TripMap.tsx
│   │   │   ├── RouteInstructions.tsx
│   │   │   └── EldLogSheet.tsx
│   │   ├── services/
│   │   │   └── api.ts
│   │   ├── types/
│   │   │   └── trip.ts
│   │   └── App.tsx
│   └── package.json
│
├── requirements.txt
└── README.md
```

## API

### Plan Trip

```http
POST /api/trips/plan/
```

Example request:

```json
{
  "current_location": "New York, NY",
  "pickup_location": "Chicago, IL",
  "dropoff_location": "Los Angeles, CA",
  "current_cycle_used": 10
}
```

The response contains:

- Geocoded locations
- Route geometry
- Route distance and duration
- Route instructions
- Duty-status events
- Planned route stops
- Cycle information
- Daily ELD logs

## Running Locally

### Backend

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.\.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run Django:

```bash
cd backend
python manage.py migrate
python manage.py runserver
```

The backend runs at:

```text
http://127.0.0.1:8000
```

### Frontend

Open another terminal:

```bash
cd frontend
npm install
```

Create:

```text
frontend/.env.local
```

with:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

Start the frontend:

```bash
npm run dev
```

The frontend is available at:

```text
http://localhost:5173
```

## Environment Variables

### Backend

```env
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=your-backend-domain
CORS_ALLOWED_ORIGINS=https://your-frontend-domain
```

### Frontend

```env
VITE_API_BASE_URL=https://your-backend-domain/api
```

## Tests

Run the backend tests with:

```bash
cd backend
python manage.py test trips
```

The test suite covers core planning scenarios including:

- 30-minute break after 8 hours of driving
- 11-hour driving limit
- 10-hour rest scheduling
- 70-hour cycle handling
- 34-hour restart
- On-duty time counting toward the cycle
- Multiple daily ELD logs
- 24-hour daily log totals
- Driving mileage split across midnight
- Fuel-stop distance boundary

## Example Test Trips

### Short Haul

```text
Current: New York, NY
Pickup: Philadelphia, PA
Dropoff: Washington, DC
Current Cycle Used: 10
```

### Cross Country

```text
Current: New York, NY
Pickup: Chicago, IL
Dropoff: Los Angeles, CA
Current Cycle Used: 10
```

### Cycle Restart

```text
Current: New York, NY
Pickup: Chicago, IL
Dropoff: Los Angeles, CA
Current Cycle Used: 68
```

## Deployment

The application is designed to be deployed using:

- **Frontend:** Vercel
- **Backend:** Render

### Live Application

To be added after deployment.

### Backend API

To be added after deployment.

## Disclaimer

This project was created as a software engineering assessment and demonstrates route planning and Hours of Service scheduling logic.

It is not a certified ELD, compliance system, or commercial truck-navigation product. Drivers and carriers should rely on applicable FMCSA regulations and approved systems for actual regulatory compliance.