from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class LocationPoint(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: str = Field(..., min_length=3)


class FareEstimateRequest(BaseModel):
    ride_type: str = Field(..., pattern=r"^(bike|auto|taxi)$")
    pickup: LocationPoint
    dropoff: LocationPoint


class FareEstimateResponse(BaseModel):
    ride_type: str
    estimated_distance_km: float
    estimated_duration_minutes: int
    estimated_fare: float
    currency: str = "INR"
    breakdown: dict


class RideBookingRequest(BaseModel):
    ride_type: str = Field(..., pattern=r"^(bike|auto|taxi)$")
    pickup: LocationPoint
    dropoff: LocationPoint
    payment_method: str = Field(default="wallet", pattern=r"^(wallet|upi|cash|card)$")
    scheduled_at: Optional[datetime] = None


class RideResponse(BaseSchema):
    id: int
    user_id: int
    driver_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    ride_type: str
    status: str
    pickup_latitude: float
    pickup_longitude: float
    pickup_address: str
    dropoff_latitude: float
    dropoff_longitude: float
    dropoff_address: str
    estimated_distance_km: Optional[float] = None
    estimated_fare: Optional[float] = None
    actual_distance_km: Optional[float] = None
    actual_fare: Optional[float] = None
    scheduled_at: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    otp_code: Optional[str] = None
    rating: Optional[int] = None
    feedback: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class RideCancelRequest(BaseModel):
    reason: str = Field(..., min_length=3, max_length=500)


class RideRatingRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    feedback: Optional[str] = Field(None, max_length=1000)


class DriverLocationUpdate(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class RideTrackingResponse(BaseModel):
    ride_id: int
    status: str
    driver_latitude: Optional[float] = None
    driver_longitude: Optional[float] = None
    pickup_latitude: float
    pickup_longitude: float
    dropoff_latitude: float
    dropoff_longitude: float
    estimated_arrival_minutes: Optional[int] = None
