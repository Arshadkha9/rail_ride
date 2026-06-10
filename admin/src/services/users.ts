import { api } from './api';
import type { ListParams, PaginatedResponse, User, UserCreate, UserUpdate } from '@/types';

const BASE = '/api/v1/admin/users';

export async function getUsers(params?: ListParams): Promise<PaginatedResponse<User>> {
  return api.get<PaginatedResponse<User>>(BASE, params);
}

export async function getUser(id: string): Promise<User> {
  return api.get<User>(`${BASE}/${id}`);
}

export async function createUser(data: UserCreate): Promise<User> {
  return api.post<User>(BASE, data);
}

export async function updateUser(id: string, data: UserUpdate): Promise<User> {
  return api.patch<User>(`${BASE}/${id}`, data);
}

export async function deleteUser(id: string): Promise<void> {
  return api.delete(`${BASE}/${id}`);
}

export async function suspendUser(id: string): Promise<User> {
  return api.post<User>(`${BASE}/${id}/suspend`);
}

export async function activateUser(id: string): Promise<User> {
  return api.post<User>(`${BASE}/${id}/activate`);
}
