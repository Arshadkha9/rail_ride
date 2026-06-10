import { api } from './api';
import type { ListParams, Notification, NotificationCreate, PaginatedResponse } from '@/types';

const BASE = '/api/v1/admin/notifications';

export async function getNotifications(
  params?: ListParams
): Promise<PaginatedResponse<Notification>> {
  return api.get<PaginatedResponse<Notification>>(BASE, params);
}

export async function getNotification(id: string): Promise<Notification> {
  return api.get<Notification>(`${BASE}/${id}`);
}

export async function createNotification(data: NotificationCreate): Promise<Notification> {
  return api.post<Notification>(BASE, data);
}

export async function sendNotification(id: string): Promise<Notification> {
  return api.post<Notification>(`${BASE}/${id}/send`);
}

export async function deleteNotification(id: string): Promise<void> {
  return api.delete(`${BASE}/${id}`);
}

export async function cancelScheduledNotification(id: string): Promise<Notification> {
  return api.post<Notification>(`${BASE}/${id}/cancel`);
}
