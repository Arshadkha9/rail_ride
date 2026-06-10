from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_admin_user
from app.core.exceptions import NotFoundError
from app.models.driver import Driver
from app.models.payment import Payment
from app.models.railway import Complaint
from app.models.ride import Ride
from app.models.user import User
from app.schemas.admin import (
    AdminRideResponse,
    ComplaintUpdateRequest,
    DashboardStats,
    DriverAdminResponse,
    DriverVerifyRequest,
    UserAdminUpdate,
)
from app.schemas.common import MessageResponse
from app.schemas.trip import ComplaintResponse
from app.schemas.user import UserResponse


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard", response_model=DashboardStats)
async def dashboard(
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    total_users = await db.execute(select(func.count()).select_from(User))
    total_drivers = await db.execute(select(func.count()).select_from(Driver))
    total_rides = await db.execute(select(func.count()).select_from(Ride))
    active_rides = await db.execute(
        select(func.count()).select_from(Ride).where(
            Ride.status.in_(["pending", "searching", "accepted", "arrived", "in_progress"])
        )
    )
    total_revenue = await db.execute(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.status == "completed")
    )
    pending_complaints = await db.execute(
        select(func.count()).select_from(Complaint).where(Complaint.status == "open")
    )

    return DashboardStats(
        total_users=total_users.scalar() or 0,
        total_drivers=total_drivers.scalar() or 0,
        total_rides=total_rides.scalar() or 0,
        active_rides=active_rides.scalar() or 0,
        total_revenue=float(total_revenue.scalar() or 0),
        pending_complaints=pending_complaints.scalar() or 0,
    )


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).order_by(User.created_at.desc()).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    payload: UserAdminUpdate,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError("User not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    await db.flush()
    return user


@router.get("/drivers", response_model=List[DriverAdminResponse])
async def list_drivers(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Driver, User)
        .join(User, User.id == Driver.user_id)
        .order_by(Driver.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    drivers = []
    for driver, user in result.all():
        drivers.append(DriverAdminResponse(
            id=driver.id,
            user_id=driver.user_id,
            license_number=driver.license_number,
            is_available=driver.is_available,
            is_verified=driver.is_verified,
            rating=driver.rating,
            total_rides=driver.total_rides,
            full_name=user.full_name,
            mobile=user.mobile,
            created_at=driver.created_at,
            updated_at=driver.updated_at,
        ))
    return drivers


@router.patch("/drivers/{driver_id}/verify", response_model=MessageResponse)
async def verify_driver(
    driver_id: int,
    payload: DriverVerifyRequest,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Driver).where(Driver.id == driver_id))
    driver = result.scalar_one_or_none()
    if not driver:
        raise NotFoundError("Driver not found")

    driver.is_verified = payload.is_verified
    await db.flush()
    return MessageResponse(message=f"Driver verification set to {payload.is_verified}")


@router.get("/rides", response_model=List[AdminRideResponse])
async def list_rides(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: str = Query(None),
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Ride)
    if status:
        query = query.where(Ride.status == status)

    result = await db.execute(
        query.order_by(Ride.created_at.desc()).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


@router.get("/complaints", response_model=List[ComplaintResponse])
async def list_all_complaints(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: str = Query(None),
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Complaint)
    if status:
        query = query.where(Complaint.status == status)

    result = await db.execute(
        query.order_by(Complaint.created_at.desc()).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


@router.patch("/complaints/{complaint_id}", response_model=ComplaintResponse)
async def update_complaint(
    complaint_id: int,
    payload: ComplaintUpdateRequest,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Complaint).where(Complaint.id == complaint_id))
    complaint = result.scalar_one_or_none()
    if not complaint:
        raise NotFoundError("Complaint not found")

    complaint.status = payload.status
    if payload.admin_response:
        complaint.admin_response = payload.admin_response
    await db.flush()
    return complaint
