from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.notification import MarkReadRequest, NotificationResponse
from app.services.notification_service import NotificationService


router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/", response_model=List[NotificationResponse])
async def list_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    notifications = await NotificationService.get_user_notifications(
        db, current_user.id, skip, limit, unread_only
    )
    return notifications


@router.get("/unread-count")
async def unread_count(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    count = await NotificationService.get_unread_count(db, current_user.id)
    return {"unread_count": count}


@router.post("/mark-read", response_model=MessageResponse)
async def mark_read(
    payload: MarkReadRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    count = await NotificationService.mark_as_read(db, current_user.id, payload.notification_ids)
    return MessageResponse(message=f"Marked {count} notifications as read")


@router.post("/mark-all-read", response_model=MessageResponse)
async def mark_all_read(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    count = await NotificationService.mark_all_as_read(db, current_user.id)
    return MessageResponse(message=f"Marked {count} notifications as read")


@router.delete("/{notification_id}", response_model=MessageResponse)
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await NotificationService.delete_notification(db, current_user.id, notification_id)
    return MessageResponse(message="Notification deleted")
