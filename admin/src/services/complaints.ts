import { api } from './api';
import type { Complaint, ComplaintUpdate, ListParams, PaginatedResponse } from '@/types';

const BASE = '/api/v1/admin/complaints';

export async function getComplaints(params?: ListParams): Promise<PaginatedResponse<Complaint>> {
  return api.get<PaginatedResponse<Complaint>>(BASE, params);
}

export async function getComplaint(id: string): Promise<Complaint> {
  return api.get<Complaint>(`${BASE}/${id}`);
}

export async function updateComplaint(id: string, data: ComplaintUpdate): Promise<Complaint> {
  return api.patch<Complaint>(`${BASE}/${id}`, data);
}

export async function assignComplaint(id: string, adminId: string): Promise<Complaint> {
  return api.post<Complaint>(`${BASE}/${id}/assign`, { admin_id: adminId });
}

export async function resolveComplaint(id: string, resolution: string): Promise<Complaint> {
  return api.post<Complaint>(`${BASE}/${id}/resolve`, { resolution });
}
