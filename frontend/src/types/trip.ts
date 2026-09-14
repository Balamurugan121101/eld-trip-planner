export interface LocationData {
  query: string;
  display_name: string;
  lat: number;
  lon: number;
}

export interface RouteGeometry {
  type: string;
  coordinates: number[][];
}

export interface RouteLeg {
  index: number;
  distance_miles: number;
  duration_minutes: number;
}

export interface RouteData {
  distance_miles: number;
  driving_minutes: number;
  driving_hours: number;
  geometry: RouteGeometry;
  legs: RouteLeg[];
}

export interface DutyEvent {
  status: "OFF" | "SB" | "D" | "ON";
  start: string;
  end: string;
  duration_minutes: number;
  reason: string;
  location: string | null;
  miles: number;
}

export interface DailyLog {
  date: string;
  events: DutyEvent[];

  totals: {
    OFF: number;
    SB: number;
    D: number;
    ON: number;
  };

  total_miles: number;
}

export interface TripPlan {
  start_time: string;
  end_time: string;
  events: DutyEvent[];
  route_stops: RouteStop[];
  daily_logs: DailyLog[];

  cycle: {
    starting_used_hours: number;
    ending_used_hours: number;
    remaining_hours: number;
  };
}

export interface TripResponse {
  locations: {
    current: LocationData;
    pickup: LocationData;
    dropoff: LocationData;
  };

  route: RouteData;

  trip_plan: TripPlan;
}

export interface RouteStop {
  type:
    | "pickup"
    | "dropoff"
    | "fuel"
    | "break"
    | "rest"
    | "restart"
    | "stop";

  reason: string;
  status: "OFF" | "SB" | "ON";

  start: string;
  end: string;

  duration_minutes: number;

  route_mile: number;

  lat: number;
  lon: number;
}

export interface RouteStep {
  instruction: string;
  distance_miles: number;
  duration_minutes: number;
  location: number[];
}

export interface RouteLeg {
  index: number;
  distance_miles: number;
  duration_minutes: number;
  steps: RouteStep[];
}