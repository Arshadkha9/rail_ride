import { api } from './api';
import type { Driver, DriverCreate, DriverUpdate, ListParams, PaginatedResponse } from '@/types';

const BASE = '/api/v1/admin/drivers';

export async function getDrivers(params?: ListParams): Promise<PaginatedResponse<Driver>> {
  return api.get<PaginatedResponse<Driver>>(BASE, params);
}

export async function getDriver(id: string): Promise<Driver> {
  return api.get<Driver>(`${BASE}/${id}`);
}

export async function createDriver(data: DriverCreate): Promise<Driver> {
  return api.post<Driver>(BASE, data);
}

export async function updateDriver(id: string, data: DriverUpdate): Promise<Driver> {
  return api.patch<Driver>(`${BASE}/${id}`, data);
}

export async function deleteDriver(id: string): Promise<void> {
  return api.delete(`${BASE}/${id}`);
}

export async function approveDriver(id: string): Promise<Driver> {
  return api.post<Driver>(`${BASE}/${id}/approve`);
}

export async function suspendDriver(id: string): Promise<Driver> {
  return api.post<Driver>(`${BASE}/${id}/suspend`);
}
