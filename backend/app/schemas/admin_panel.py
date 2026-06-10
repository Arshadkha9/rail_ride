from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str


class AdminUserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str = "admin"


class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    admin: AdminUserResponse


class AdminUserItem(BaseModel):
    id: str
    email: str
    full_name: str
    phone: str
    status: str
    total_rides: int
    created_at: datetime
    last_active_at: Optional[datetime] = None


class AdminUserCreate(BaseModel):
    email: EmailStr
    full_name: str
    phone: str
    password: str = Field(..., min_length=6)


class AdminUserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None


class AdminDriverItem(BaseModel):
    id: str
    email: str
    full_name: str
    phone: str
    license_number: str
    vehicle_model: str
    vehicle_plate: str
    status: str
    rating: float
    total_rides: int
    created_at: datetime


class AdminDriverCreate(BaseModel):
    email: EmailStr
    full_name: str
    phone: str
    license_number: str
    vehicle_model: str
    vehicle_plate: str
    password: str = Field(..., min_length=6)


class AdminDriverUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_plate: Optional[str] = None
    status: Optional[str] = None


class RideLocationResponse(BaseModel):
    lat: float
    lng: float
    address: str


class AdminRideItem(BaseModel):
    id: str
    user_id: str
    user_name: str
    driver_id: Optional[str] = None
    driver_name: Optional[str] = None
    pickup: RideLocationResponse
    dropoff: RideLocationResponse
    status: str
    fare: float
    distance_km: float
    duration_minutes: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class AdminLiveRideItem(AdminRideItem):
    current_lat: Optional[float] = None
    current_lng: Optional[float] = None


class AdminDashboardStats(BaseModel):
    total_users: int
    total_drivers: int
    active_rides: int
    today_revenue: float
    pending_complaints: int
    online_drivers: int


class RevenueSummary(BaseModel):
    total_revenue: float
    today_revenue: float
    week_revenue: float
    month_revenue: float
    total_rides: int
    average_fare: float
    commission_earned: float


class RevenueDataPoint(BaseModel):
    date: str
    revenue: float
    rides: int


class RevenueAnalytics(BaseModel):
    summary: RevenueSummary
    daily: List[RevenueDataPoint]
    monthly: List[RevenueDataPoint]


class AdminBroadcastNotification(BaseModel):
    id: str
    title: str
    message: str
    target: str
    status: str
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    recipient_count: int
    created_at: datetime


class AdminBroadcastCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    target: str = Field(..., pattern=r"^(all_users|all_drivers|specific_users|specific_drivers)$")
    target_ids: Optional[List[str]] = None
    scheduled_at: Optional[datetime] = None


class AdminComplaintItem(BaseModel):
    id: str
    user_id: str
    user_name: str
    ride_id: Optional[str] = None
    subject: str
    description: str
    status: str
    priority: str
    assigned_to: Optional[str] = None
    resolution: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class AdminComplaintUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[str] = None
    resolution: Optional[str] = None


class RideCancelRequest(BaseModel):
    reason: str = Field(..., min_length=3)
