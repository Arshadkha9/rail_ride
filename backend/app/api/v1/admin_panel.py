from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_admin_user
from app.models.user import User
from app.schemas.admin_panel import (
    AdminBroadcastCreate,
    AdminBroadcastNotification,
    AdminComplaintItem,
    AdminComplaintUpdate,
    AdminDashboardStats,
    AdminDriverCreate,
    AdminDriverItem,
    AdminDriverUpdate,
    AdminLiveRideItem,
    AdminRideItem,
    AdminUserCreate,
    AdminUserItem,
    AdminUserUpdate,
    RevenueAnalytics,
    RideCancelRequest,
)
from app.schemas.common import MessageResponse
from app.schemas.pagination import PaginatedResponse
from app.services.admin_panel_service import AdminPanelService


router = APIRouter(prefix="/admin", tags=["Admin Panel"])


@router.get("/dashboard/stats", response_model=AdminDashboardStats)
async def dashboard_stats(
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    return await AdminPanelService.dashboard_stats(db)


@router.get("/users", response_model=PaginatedResponse[AdminUserItem])
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    return await AdminPanelService.list_users(db, page, page_size, search, status)


@router.post("/users", response_model=AdminUserItem, status_code=201)
async def create_user(
    payload: AdminUserCreate,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    return await AdminPanelService.create_user(db, payload)


@router.get("/users/{user_id}", response_model=AdminUserItem)
async def get_user(
    user_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    return await AdminPanelService.get_user(db, user_id)


@router.patch("/users/{user_id}", response_model=AdminUserItem)
async def update_user(
    user_id: int,
    payload: AdminUserUpdate,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    return await AdminPanelService.update_user(db, user_id, payload)


@router.delete("/users/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    await AdminPanelService.delete_user(db, user_id)
    return MessageResponse(message="User deleted")


@router.post("/users/{user_id}/suspend", response_model=AdminUserItem)
async def suspend_user(
    user_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    return await AdminPanelService.suspend_user(db, user_id)


@router.post("/users/{user_id}/activate", response_model=AdminUserItem)
async def activate_user(
    user_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    return await AdminPanelService.activate_user(db, user_id)


@router.get("/drivers", response_model=PaginatedResponse[AdminDriverItem])
async def list_drivers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    return await AdminPanelService.list_drivers(db, page, page_size, search, status)


@router.post("/drivers", response_model=AdminDriverItem, status_code=201)
async def create_driver(
    payload: AdminDriverCreate,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    return await AdminPanelService.create_driver(db, payload)


@router.get("/drivers/{driver_id}", response_model=AdminDriverItem)
async def get_driver(
    driver_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    return await AdminPanelService.get_driver(db, driver_id)


@router.patch("/drivers/{driver_id}", response_model=AdminDriverItem)
async def update_driver(
    driver_id: int,
    payload: AdminDriverUpdate,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    return await AdminPanelService.update_driver(db, driver_id, payload)


@router.delete("/drivers/{driver_id}", response_model=MessageResponse)
async def delete_driver(
    driver_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    await AdminPanelService.delete_driver(db, driver_id)
    return MessageResponse(message="Driver deleted")


@router.post("/drivers/{driver_id}/approve", response_model=AdminDriverItem)
async def approve_driver(
    driver_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    return await AdminPanelService.approve_driver(db, driver_id)


@router.post("/drivers/{driver_id}/suspend", response_model=AdminDriverItem)
async def suspend_driver(
    driver_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    return await AdminPanelService.suspend_driver(db, driver_id)


@router.get("/rides", response_model=PaginatedResponse[AdminRideItem])
async def list_rides(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    return await AdminPanelService.list_rides(db, page, page_size, status)


@router.get("/rides/live", response_model=List[AdminLiveRideItem])
async def live_rides(
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    return await AdminPanelService.live_rides(db)


@router.get("/rides/{ride_id}", response_model=AdminRideItem)
async def get_ride(
    ride_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    return await AdminPanelService.get_ride(db, ride_id)


@router.post("/rides/{ride_id}/cancel", response_model=AdminRideItem)
async def cancel_ride(
    ride_id: int,
    payload: RideCancelRequest,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    return await AdminPanelService.cancel_ride(db, ride_id, payload.reason)


@router.get("/revenue", response_model=RevenueAnalytics)
async def revenue_analytics(
    period: str = Query("30d", pattern=r"^(7d|30d|90d|1y)$"),
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    return await AdminPanelService.revenue_analytics(db, period)


@router.get("/revenue/export")
async def export_revenue(
    period: str = Query("30d", pattern=r"^(7d|30d|90d|1y)$"),
    format: str = Query("csv", pattern=r"^(csv|pdf)$"),
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    if format == "pdf":
        return PlainTextResponse("PDF export not implemented", status_code=501)
    csv_data = await AdminPanelService.export_revenue_csv(db, period)
    return PlainTextResponse(
        csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=revenue_{period}.csv"},
    )


@router.get("/notifications", response_model=PaginatedResponse[AdminBroadcastNotification])
async def list_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    return await AdminPanelService.list_broadcasts(db, page, page_size)


@router.post("/notifications", response_model=AdminBroadcastNotification, status_code=201)
async def create_notification(
    payload: AdminBroadcastCreate,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    return await AdminPanelService.create_broadcast(db, payload)


@router.get("/notifications/{notification_id}", response_model=AdminBroadcastNotification)
async def get_notification(
    notification_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    return await AdminPanelService.get_broadcast(db, notification_id)


@router.post("/notifications/{notification_id}/send", response_model=AdminBroadcastNotification)
async def send_notification(
    notification_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    return await AdminPanelService.send_broadcast(db, notification_id)


@router.post("/notifications/{notification_id}/cancel", response_model=AdminBroadcastNotification)
async def cancel_notification(
    notification_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    return await AdminPanelService.cancel_broadcast(db, notification_id)


@router.delete("/notifications/{notification_id}", response_model=MessageResponse)
async def delete_notification(
    notification_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    await AdminPanelService.delete_broadcast(db, notification_id)
    return MessageResponse(message="Notification deleted")


@router.get("/complaints", response_model=PaginatedResponse[AdminComplaintItem])
async def list_complaints(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    search: Optional[str] = None,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    return await AdminPanelService.list_complaints(db, page, page_size, status, search)


@router.patch("/complaints/{complaint_id}", response_model=AdminComplaintItem)
async def update_complaint(
    complaint_id: int,
    payload: AdminComplaintUpdate,
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    return await AdminPanelService.update_complaint(db, complaint_id, payload)
