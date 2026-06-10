import { api, setToken, clearToken } from './api';
import type { AdminUser, LoginRequest, LoginResponse } from '@/types';

const ADMIN_PREFIX = '/api/v1/admin';

export async function login(credentials: LoginRequest): Promise<LoginResponse> {
  const response = await api.post<LoginResponse>(`${ADMIN_PREFIX}/auth/login`, credentials);
  setToken(response.access_token);
  return response;
}

export async function logout(): Promise<void> {
  try {
    await api.post(`${ADMIN_PREFIX}/auth/logout`);
  } finally {
    clearToken();
  }
}

export async function getCurrentAdmin(): Promise<AdminUser> {
  return api.get<AdminUser>(`${ADMIN_PREFIX}/auth/me`);
}

export async function refreshToken(): Promise<LoginResponse> {
  const response = await api.post<LoginResponse>(`${ADMIN_PREFIX}/auth/refresh`);
  setToken(response.access_token);
  return response;
}
