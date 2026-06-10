from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema
from app.schemas.user import UserResponse


class DashboardStats(BaseModel):
    total_users: int
    total_drivers: int
    total_rides: int
    active_rides: int
    total_revenue: float
    pending_complaints: int


class DriverAdminResponse(BaseSchema):
    id: int
    user_id: int
    license_number: str
    is_available: bool
    is_verified: bool
    rating: float
    total_rides: int
    full_name: Optional[str] = None
    mobile: Optional[str] = None


class DriverVerifyRequest(BaseModel):
    is_verified: bool


class ComplaintUpdateRequest(BaseModel):
    status: str = Field(..., pattern=r"^(open|in_progress|resolved|closed)$")
    admin_response: Optional[str] = None


class UserAdminUpdate(BaseModel):
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    is_verified: Optional[bool] = None


class AdminRideResponse(BaseSchema):
    id: int
    user_id: int
    driver_id: Optional[int] = None
    ride_type: str
    status: str
    estimated_fare: Optional[float] = None
    actual_fare: Optional[float] = None
    created_at: datetime
