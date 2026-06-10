from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.railway import Complaint, TripHistory
from app.models.user import User
from app.schemas.trip import ComplaintCreate, ComplaintResponse, TripHistoryResponse


router = APIRouter(prefix="/trips", tags=["Trips"])


@router.get("/history", response_model=List[TripHistoryResponse])
async def trip_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    trip_type: str = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(TripHistory).where(TripHistory.user_id == current_user.id)

    if trip_type:
        query = query.where(TripHistory.trip_type == trip_type)

    result = await db.execute(
        query.order_by(TripHistory.trip_date.desc()).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


@router.get("/history/{trip_id}", response_model=TripHistoryResponse)
async def get_trip(
    trip_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TripHistory).where(
            TripHistory.id == trip_id,
            TripHistory.user_id == current_user.id,
        )
    )
    trip = result.scalar_one_or_none()
    if not trip:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Trip not found")
    return trip


@router.post("/complaints", response_model=ComplaintResponse, status_code=201)
async def create_complaint(
    payload: ComplaintCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    complaint = Complaint(
        user_id=current_user.id,
        category=payload.category,
        subject=payload.subject,
        description=payload.description,
        reference_type=payload.reference_type,
        reference_id=payload.reference_id,
    )
    db.add(complaint)
    await db.flush()
    return complaint


@router.get("/complaints", response_model=List[ComplaintResponse])
async def list_complaints(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Complaint)
        .where(Complaint.user_id == current_user.id)
        .order_by(Complaint.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


@router.get("/complaints/{complaint_id}", response_model=ComplaintResponse)
async def get_complaint(
    complaint_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Complaint).where(
            Complaint.id == complaint_id,
            Complaint.user_id == current_user.id,
        )
    )
    complaint = result.scalar_one_or_none()
    if not complaint:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Complaint not found")
    return complaint
