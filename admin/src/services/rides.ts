import { api } from './api';
import type { DashboardStats, ListParams, LiveRide, PaginatedResponse, Ride } from '@/types';

const BASE = '/api/v1/admin/rides';

export async function getRides(params?: ListParams): Promise<PaginatedResponse<Ride>> {
  return api.get<PaginatedResponse<Ride>>(BASE, params);
}

export async function getRide(id: string): Promise<Ride> {
  return api.get<Ride>(`${BASE}/${id}`);
}

export async function getLiveRides(): Promise<LiveRide[]> {
  return api.get<LiveRide[]>(`${BASE}/live`);
}

export async function cancelRide(id: string, reason: string): Promise<Ride> {
  return api.post<Ride>(`${BASE}/${id}/cancel`, { reason });
}

export async function getDashboardStats(): Promise<DashboardStats> {
  return api.get<DashboardStats>('/api/v1/admin/dashboard/stats');
}
