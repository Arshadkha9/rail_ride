from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.ride import (
    FareEstimateRequest,
    FareEstimateResponse,
    RideBookingRequest,
    RideCancelRequest,
    RideRatingRequest,
    RideResponse,
    RideTrackingResponse,
)
from app.services.ride_service import RideService


router = APIRouter(prefix="/rides", tags=["Rides"])


@router.post("/estimate", response_model=FareEstimateResponse)
async def estimate_fare(payload: FareEstimateRequest):
    result = await RideService.estimate(
        payload.ride_type,
        payload.pickup.latitude,
        payload.pickup.longitude,
        payload.dropoff.latitude,
        payload.dropoff.longitude,
    )
    return result


@router.post("/book", response_model=RideResponse, status_code=201)
async def book_ride(
    payload: RideBookingRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    ride = await RideService.book_ride(
        db,
        current_user,
        payload.ride_type,
        payload.pickup.latitude,
        payload.pickup.longitude,
        payload.pickup.address,
        payload.dropoff.latitude,
        payload.dropoff.longitude,
        payload.dropoff.address,
        payload.payment_method,
        payload.scheduled_at,
    )
    return ride


@router.get("/", response_model=List[RideResponse])
async def list_rides(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    rides = await RideService.get_user_rides(db, current_user.id, skip, limit)
    return rides


@router.get("/{ride_id}", response_model=RideResponse)
async def get_ride(
    ride_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    ride = await RideService.get_ride(db, ride_id, current_user.id)
    return ride


@router.get("/{ride_id}/track", response_model=RideTrackingResponse)
async def track_ride(
    ride_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    ride = await RideService.get_ride(db, ride_id, current_user.id)
    tracking = await RideService.get_tracking_info(db, ride)
    return tracking


@router.post("/{ride_id}/cancel", response_model=RideResponse)
async def cancel_ride(
    ride_id: int,
    payload: RideCancelRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    ride = await RideService.get_ride(db, ride_id, current_user.id)
    ride = await RideService.cancel_ride(db, ride, payload.reason)
    return ride


@router.post("/{ride_id}/complete", response_model=RideResponse)
async def complete_ride(
    ride_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    ride = await RideService.get_ride(db, ride_id, current_user.id)
    ride = await RideService.complete_ride(db, ride)
    return ride


@router.post("/{ride_id}/rate", response_model=RideResponse)
async def rate_ride(
    ride_id: int,
    payload: RideRatingRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    ride = await RideService.get_ride(db, ride_id, current_user.id)
    ride = await RideService.rate_ride(db, ride, payload.rating, payload.feedback)
    return ride
