export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ValidationErrorItem {
  msg?: string;
  loc?: (string | number)[];
  type?: string;
}

export interface ApiError {
  detail: string | ValidationErrorItem[];
  status_code?: number;
}

export interface AdminUser {
  id: string;
  email: string;
  full_name: string;
  role: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  admin: AdminUser;
}

export type UserStatus = 'active' | 'inactive' | 'suspended' | 'pending';

export interface User {
  id: string;
  email: string;
  full_name: string;
  phone: string;
  status: UserStatus;
  total_rides: number;
  created_at: string;
  last_active_at: string | null;
}

export interface UserCreate {
  email: string;
  full_name: string;
  phone: string;
  password: string;
}

export interface UserUpdate {
  full_name?: string;
  phone?: string;
  status?: UserStatus;
}

export type DriverStatus = 'online' | 'offline' | 'on_ride' | 'suspended' | 'pending_approval';

export interface Driver {
  id: string;
  email: string;
  full_name: string;
  phone: string;
  license_number: string;
  vehicle_model: string;
  vehicle_plate: string;
  status: DriverStatus;
  rating: number;
  total_rides: number;
  created_at: string;
}

export interface DriverCreate {
  email: string;
  full_name: string;
  phone: string;
  license_number: string;
  vehicle_model: string;
  vehicle_plate: string;
  password: string;
}

export interface DriverUpdate {
  full_name?: string;
  phone?: string;
  vehicle_model?: string;
  vehicle_plate?: string;
  status?: DriverStatus;
}

export type RideStatus = 'requested' | 'accepted' | 'in_progress' | 'completed' | 'cancelled';

export interface RideLocation {
  lat: number;
  lng: number;
  address: string;
}

export interface Ride {
  id: string;
  user_id: string;
  user_name: string;
  driver_id: string | null;
  driver_name: string | null;
  pickup: RideLocation;
  dropoff: RideLocation;
  status: RideStatus;
  fare: number;
  distance_km: number;
  duration_minutes: number;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}

export interface LiveRide extends Ride {
  current_lat: number | null;
  current_lng: number | null;
}

export interface RevenueSummary {
  total_revenue: number;
  today_revenue: number;
  week_revenue: number;
  month_revenue: number;
  total_rides: number;
  average_fare: number;
  commission_earned: number;
}

export interface RevenueDataPoint {
  date: string;
  revenue: number;
  rides: number;
}

export interface RevenueAnalytics {
  summary: RevenueSummary;
  daily: RevenueDataPoint[];
  monthly: RevenueDataPoint[];
}

export type NotificationStatus = 'draft' | 'scheduled' | 'sent' | 'failed';
export type NotificationTarget = 'all_users' | 'all_drivers' | 'specific_users' | 'specific_drivers';

export interface Notification {
  id: string;
  title: string;
  message: string;
  target: NotificationTarget;
  status: NotificationStatus;
  scheduled_at: string | null;
  sent_at: string | null;
  recipient_count: number;
  created_at: string;
}

export interface NotificationCreate {
  title: string;
  message: string;
  target: NotificationTarget;
  target_ids?: string[];
  scheduled_at?: string;
}

export type ComplaintStatus = 'open' | 'in_review' | 'resolved' | 'closed';
export type ComplaintPriority = 'low' | 'medium' | 'high' | 'urgent';

export interface Complaint {
  id: string;
  user_id: string;
  user_name: string;
  ride_id: string | null;
  subject: string;
  description: string;
  status: ComplaintStatus;
  priority: ComplaintPriority;
  assigned_to: string | null;
  resolution: string | null;
  created_at: string;
  updated_at: string;
}

export interface ComplaintUpdate {
  status?: ComplaintStatus;
  priority?: ComplaintPriority;
  assigned_to?: string;
  resolution?: string;
}

export interface DashboardStats {
  total_users: number;
  total_drivers: number;
  active_rides: number;
  today_revenue: number;
  pending_complaints: number;
  online_drivers: number;
}

export interface ListParams {
  page?: number;
  page_size?: number;
  search?: string;
  status?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  [key: string]: string | number | boolean | undefined;
}
