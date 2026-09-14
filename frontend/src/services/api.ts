import axios from "axios";
import type { TripResponse } from "../types/trip";

const api = axios.create({
  baseURL:
    import.meta.env.VITE_API_BASE_URL ||
    "http://127.0.0.1:8000/api",
});

export interface TripRequest {
  current_location: string;
  pickup_location: string;
  dropoff_location: string;
  current_cycle_used: number;
}

export async function planTrip(
  request: TripRequest
): Promise<TripResponse> {
  const response = await api.post<TripResponse>(
    "/trips/plan/",
    request
  );

  return response.data;
}