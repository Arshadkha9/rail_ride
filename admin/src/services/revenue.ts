import { api } from './api';
import type { RevenueAnalytics } from '@/types';

const BASE = '/api/v1/admin/revenue';

export async function getRevenueAnalytics(
  period: '7d' | '30d' | '90d' | '1y' = '30d'
): Promise<RevenueAnalytics> {
  return api.get<RevenueAnalytics>(BASE, { period });
}

export async function exportRevenueReport(
  period: '7d' | '30d' | '90d' | '1y' = '30d',
  format: 'csv' | 'pdf' = 'csv'
): Promise<Blob> {
  const base = import.meta.env.VITE_API_URL?.replace(/\/$/, '') ?? '';
  const url = new URL(`${base}${BASE}/export`, window.location.origin);
  url.searchParams.set('period', period);
  url.searchParams.set('format', format);

  const token = localStorage.getItem('railride_admin_token');
  const response = await fetch(url.toString(), {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });

  if (!response.ok) {
    throw new Error('Failed to export revenue report');
  }

  return response.blob();
}
