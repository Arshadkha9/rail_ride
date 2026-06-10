import csv
import io
import json
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.core.security import get_password_hash
from app.models.broadcast_notification import BroadcastNotification
from app.models.driver import Driver
from app.models.payment import Payment
from app.models.railway import Complaint
from app.models.ride import Ride
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.wallet import Wallet
from app.schemas.admin_panel import (
    AdminBroadcastNotification,
    AdminComplaintItem,
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
    RevenueDataPoint,
    RevenueSummary,
    RideLocationResponse,
)
from app.schemas.pagination import PaginatedResponse, paginate


def _user_status(user: User) -> str:
    if not user.is_active:
        return "suspended"
    if not user.is_verified:
        return "pending"
    return "active"


def _driver_status(driver: Driver) -> str:
    if not driver.is_verified:
        return "pending_approval"
    if not driver.is_available:
        return "offline"
    return "online"


def _map_ride_status(status: str) -> str:
    mapping = {
        "pending": "requested",
        "searching": "requested",
        "accepted": "accepted",
        "arrived": "accepted",
        "in_progress": "in_progress",
        "completed": "completed",
        "cancelled": "cancelled",
    }
    return mapping.get(status, status)


class AdminPanelService:
    @staticmethod
    async def dashboard_stats(db: AsyncSession) -> AdminDashboardStats:
        now = datetime.now(timezone.utc)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

        total_users = (await db.execute(select(func.count()).select_from(User).where(User.is_admin.is_(False)))).scalar() or 0
        total_drivers = (await db.execute(select(func.count()).select_from(Driver))).scalar() or 0
        active_rides = (
            await db.execute(
                select(func.count()).select_from(Ride).where(
                    Ride.status.in_(["pending", "searching", "accepted", "arrived", "in_progress"])
                )
            )
        ).scalar() or 0
        online_drivers = (
            await db.execute(select(func.count()).select_from(Driver).where(Driver.is_available.is_(True)))
        ).scalar() or 0
        today_revenue = (
            await db.execute(
                select(func.coalesce(func.sum(Payment.amount), 0)).where(
                    Payment.status == "completed",
                    Payment.created_at >= start_of_day,
                )
            )
        ).scalar() or 0
        pending_complaints = (
            await db.execute(select(func.count()).select_from(Complaint).where(Complaint.status == "open"))
        ).scalar() or 0

        return AdminDashboardStats(
            total_users=total_users,
            total_drivers=total_drivers,
            active_rides=active_rides,
            today_revenue=float(today_revenue),
            pending_complaints=pending_complaints,
            online_drivers=online_drivers,
        )

    @staticmethod
    async def list_users(
        db: AsyncSession,
        page: int,
        page_size: int,
        search: Optional[str] = None,
        status: Optional[str] = None,
    ) -> PaginatedResponse[AdminUserItem]:
        query = select(User).where(User.is_admin.is_(False))
        if search:
            pattern = f"%{search}%"
            query = query.where(
                or_(User.full_name.ilike(pattern), User.email.ilike(pattern), User.mobile.ilike(pattern))
            )
        if status == "active":
            query = query.where(User.is_active.is_(True), User.is_verified.is_(True))
        elif status == "suspended":
            query = query.where(User.is_active.is_(False))
        elif status == "pending":
            query = query.where(User.is_verified.is_(False))

        total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
        result = await db.execute(
            query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        )
        users = result.scalars().all()

        items: List[AdminUserItem] = []
        for user in users:
            ride_count = (
                await db.execute(select(func.count()).select_from(Ride).where(Ride.user_id == user.id))
            ).scalar() or 0
            items.append(
                AdminUserItem(
                    id=str(user.id),
                    email=user.email or "",
                    full_name=user.full_name,
                    phone=user.mobile or "",
                    status=_user_status(user),
                    total_rides=ride_count,
                    created_at=user.created_at,
                    last_active_at=user.updated_at,
                )
            )
        return paginate(items, total, page, page_size)

    @staticmethod
    async def create_user(db: AsyncSession, payload: AdminUserCreate) -> AdminUserItem:
        existing = await db.execute(select(User).where(User.email == payload.email))
        if existing.scalar_one_or_none():
            raise ConflictError("Email already registered")

        user = User(
            full_name=payload.full_name,
            email=payload.email,
            mobile=payload.phone,
            password_hash=get_password_hash(payload.password),
            is_verified=True,
            is_active=True,
        )
        db.add(user)
        await db.flush()
        db.add(Wallet(user_id=user.id, balance=0.0))
        await db.flush()
        return AdminUserItem(
            id=str(user.id),
            email=user.email or "",
            full_name=user.full_name,
            phone=user.mobile or "",
            status="active",
            total_rides=0,
            created_at=user.created_at,
            last_active_at=user.updated_at,
        )

    @staticmethod
    async def get_user(db: AsyncSession, user_id: int) -> AdminUserItem:
        user = await AdminPanelService._get_user(db, user_id)
        ride_count = (
            await db.execute(select(func.count()).select_from(Ride).where(Ride.user_id == user.id))
        ).scalar() or 0
        return AdminUserItem(
            id=str(user.id),
            email=user.email or "",
            full_name=user.full_name,
            phone=user.mobile or "",
            status=_user_status(user),
            total_rides=ride_count,
            created_at=user.created_at,
            last_active_at=user.updated_at,
        )

    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, payload: AdminUserUpdate) -> AdminUserItem:
        user = await AdminPanelService._get_user(db, user_id)
        if payload.full_name is not None:
            user.full_name = payload.full_name
        if payload.phone is not None:
            user.mobile = payload.phone
        if payload.status == "active":
            user.is_active = True
            user.is_verified = True
        elif payload.status == "suspended":
            user.is_active = False
        elif payload.status == "inactive":
            user.is_active = False
        await db.flush()
        return await AdminPanelService.get_user(db, user_id)

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int) -> None:
        user = await AdminPanelService._get_user(db, user_id)
        await db.delete(user)

    @staticmethod
    async def suspend_user(db: AsyncSession, user_id: int) -> AdminUserItem:
        user = await AdminPanelService._get_user(db, user_id)
        user.is_active = False
        await db.flush()
        return await AdminPanelService.get_user(db, user_id)

    @staticmethod
    async def activate_user(db: AsyncSession, user_id: int) -> AdminUserItem:
        user = await AdminPanelService._get_user(db, user_id)
        user.is_active = True
        user.is_verified = True
        await db.flush()
        return await AdminPanelService.get_user(db, user_id)

    @staticmethod
    async def _get_user(db: AsyncSession, user_id: int) -> User:
        result = await db.execute(select(User).where(User.id == user_id, User.is_admin.is_(False)))
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundError("User not found")
        return user

    @staticmethod
    async def _driver_to_item(db: AsyncSession, driver: Driver, user: User) -> AdminDriverItem:
        vehicle_result = await db.execute(
            select(Vehicle).where(Vehicle.driver_id == driver.id).limit(1)
        )
        vehicle = vehicle_result.scalar_one_or_none()
        return AdminDriverItem(
            id=str(driver.id),
            email=user.email or "",
            full_name=user.full_name,
            phone=user.mobile or "",
            license_number=driver.license_number,
            vehicle_model=vehicle.model if vehicle else "N/A",
            vehicle_plate=vehicle.registration_number if vehicle else "N/A",
            status=_driver_status(driver),
            rating=driver.rating,
            total_rides=driver.total_rides,
            created_at=driver.created_at,
        )

    @staticmethod
    async def list_drivers(
        db: AsyncSession,
        page: int,
        page_size: int,
        search: Optional[str] = None,
        status: Optional[str] = None,
    ) -> PaginatedResponse[AdminDriverItem]:
        query = select(Driver, User).join(User, User.id == Driver.user_id)
        if search:
            pattern = f"%{search}%"
            query = query.where(
                or_(User.full_name.ilike(pattern), User.email.ilike(pattern), Driver.license_number.ilike(pattern))
            )
        if status == "pending_approval":
            query = query.where(Driver.is_verified.is_(False))
        elif status == "online":
            query = query.where(Driver.is_available.is_(True), Driver.is_verified.is_(True))
        elif status == "offline":
            query = query.where(Driver.is_available.is_(False))

        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar() or 0
        result = await db.execute(
            query.order_by(Driver.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        )

        items = []
        for driver, user in result.all():
            items.append(await AdminPanelService._driver_to_item(db, driver, user))
        return paginate(items, total, page, page_size)

    @staticmethod
    async def create_driver(db: AsyncSession, payload: AdminDriverCreate) -> AdminDriverItem:
        existing = await db.execute(select(User).where(User.email == payload.email))
        if existing.scalar_one_or_none():
            raise ConflictError("Email already registered")

        user = User(
            full_name=payload.full_name,
            email=payload.email,
            mobile=payload.phone,
            password_hash=get_password_hash(payload.password),
            is_verified=True,
            is_active=True,
        )
        db.add(user)
        await db.flush()

        driver = Driver(
            user_id=user.id,
            license_number=payload.license_number,
            is_verified=True,
            is_available=False,
        )
        db.add(driver)
        await db.flush()

        vehicle = Vehicle(
            driver_id=driver.id,
            vehicle_type="auto",
            make="Generic",
            model=payload.vehicle_model,
            registration_number=payload.vehicle_plate,
            color="White",
            year=2022,
        )
        db.add(vehicle)
        await db.flush()
        return await AdminPanelService._driver_to_item(db, driver, user)

    @staticmethod
    async def get_driver(db: AsyncSession, driver_id: int) -> AdminDriverItem:
        driver, user = await AdminPanelService._get_driver_with_user(db, driver_id)
        return await AdminPanelService._driver_to_item(db, driver, user)

    @staticmethod
    async def update_driver(db: AsyncSession, driver_id: int, payload: AdminDriverUpdate) -> AdminDriverItem:
        driver, user = await AdminPanelService._get_driver_with_user(db, driver_id)
        if payload.full_name is not None:
            user.full_name = payload.full_name
        if payload.phone is not None:
            user.mobile = payload.phone
        if payload.status == "online":
            driver.is_available = True
            driver.is_verified = True
        elif payload.status == "offline":
            driver.is_available = False
        elif payload.status == "suspended":
            driver.is_available = False
            user.is_active = False
        elif payload.status == "pending_approval":
            driver.is_verified = False

        if payload.vehicle_model or payload.vehicle_plate:
            vehicle_result = await db.execute(select(Vehicle).where(Vehicle.driver_id == driver.id).limit(1))
            vehicle = vehicle_result.scalar_one_or_none()
            if vehicle:
                if payload.vehicle_model:
                    vehicle.model = payload.vehicle_model
                if payload.vehicle_plate:
                    vehicle.registration_number = payload.vehicle_plate

        await db.flush()
        return await AdminPanelService._driver_to_item(db, driver, user)

    @staticmethod
    async def delete_driver(db: AsyncSession, driver_id: int) -> None:
        driver, user = await AdminPanelService._get_driver_with_user(db, driver_id)
        await db.delete(driver)
        await db.delete(user)

    @staticmethod
    async def approve_driver(db: AsyncSession, driver_id: int) -> AdminDriverItem:
        driver, user = await AdminPanelService._get_driver_with_user(db, driver_id)
        driver.is_verified = True
        await db.flush()
        return await AdminPanelService._driver_to_item(db, driver, user)

    @staticmethod
    async def suspend_driver(db: AsyncSession, driver_id: int) -> AdminDriverItem:
        driver, user = await AdminPanelService._get_driver_with_user(db, driver_id)
        driver.is_available = False
        user.is_active = False
        await db.flush()
        return await AdminPanelService._driver_to_item(db, driver, user)

    @staticmethod
    async def _get_driver_with_user(db: AsyncSession, driver_id: int) -> Tuple[Driver, User]:
        result = await db.execute(
            select(Driver, User).join(User, User.id == Driver.user_id).where(Driver.id == driver_id)
        )
        row = result.one_or_none()
        if not row:
            raise NotFoundError("Driver not found")
        return row[0], row[1]

    @staticmethod
    async def _ride_to_item(db: AsyncSession, ride: Ride) -> AdminRideItem:
        user_result = await db.execute(select(User).where(User.id == ride.user_id))
        user = user_result.scalar_one()
        driver_name = None
        if ride.driver_id:
            driver_result = await db.execute(
                select(Driver, User)
                .join(User, User.id == Driver.user_id)
                .where(Driver.id == ride.driver_id)
            )
            row = driver_result.one_or_none()
            if row:
                driver_name = row[1].full_name

        fare = ride.actual_fare or ride.estimated_fare or 0.0
        distance = ride.actual_distance_km or ride.estimated_distance_km or 0.0
        duration = 0
        if ride.started_at and ride.completed_at:
            duration = int((ride.completed_at - ride.started_at).total_seconds() / 60)

        return AdminRideItem(
            id=str(ride.id),
            user_id=str(ride.user_id),
            user_name=user.full_name,
            driver_id=str(ride.driver_id) if ride.driver_id else None,
            driver_name=driver_name,
            pickup=RideLocationResponse(
                lat=ride.pickup_latitude,
                lng=ride.pickup_longitude,
                address=ride.pickup_address,
            ),
            dropoff=RideLocationResponse(
                lat=ride.dropoff_latitude,
                lng=ride.dropoff_longitude,
                address=ride.dropoff_address,
            ),
            status=_map_ride_status(ride.status),
            fare=fare,
            distance_km=distance,
            duration_minutes=duration,
            created_at=ride.created_at,
            started_at=ride.started_at,
            completed_at=ride.completed_at,
        )

    @staticmethod
    async def list_rides(
        db: AsyncSession,
        page: int,
        page_size: int,
        status: Optional[str] = None,
    ) -> PaginatedResponse[AdminRideItem]:
        query = select(Ride)
        if status:
            reverse_map = {
                "requested": ["pending", "searching"],
                "accepted": ["accepted", "arrived"],
                "in_progress": ["in_progress"],
                "completed": ["completed"],
                "cancelled": ["cancelled"],
            }
            statuses = reverse_map.get(status, [status])
            query = query.where(Ride.status.in_(statuses))

        total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
        result = await db.execute(
            query.order_by(Ride.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        )
        rides = result.scalars().all()
        items = [await AdminPanelService._ride_to_item(db, ride) for ride in rides]
        return paginate(items, total, page, page_size)

    @staticmethod
    async def get_ride(db: AsyncSession, ride_id: int) -> AdminRideItem:
        result = await db.execute(select(Ride).where(Ride.id == ride_id))
        ride = result.scalar_one_or_none()
        if not ride:
            raise NotFoundError("Ride not found")
        return await AdminPanelService._ride_to_item(db, ride)

    @staticmethod
    async def live_rides(db: AsyncSession) -> List[AdminLiveRideItem]:
        result = await db.execute(
            select(Ride).where(Ride.status.in_(["accepted", "arrived", "in_progress"]))
        )
        rides = result.scalars().all()
        items: List[AdminLiveRideItem] = []
        for ride in rides:
            base = await AdminPanelService._ride_to_item(db, ride)
            current_lat, current_lng = None, None
            if ride.driver_id:
                driver_result = await db.execute(select(Driver).where(Driver.id == ride.driver_id))
                driver = driver_result.scalar_one_or_none()
                if driver:
                    current_lat = driver.current_latitude
                    current_lng = driver.current_longitude
            items.append(
                AdminLiveRideItem(
                    **base.model_dump(),
                    current_lat=current_lat,
                    current_lng=current_lng,
                )
            )
        return items

    @staticmethod
    async def cancel_ride(db: AsyncSession, ride_id: int, reason: str) -> AdminRideItem:
        result = await db.execute(select(Ride).where(Ride.id == ride_id))
        ride = result.scalar_one_or_none()
        if not ride:
            raise NotFoundError("Ride not found")
        ride.status = "cancelled"
        ride.cancellation_reason = reason
        ride.cancelled_at = datetime.now(timezone.utc)
        await db.flush()
        return await AdminPanelService._ride_to_item(db, ride)

    @staticmethod
    async def revenue_analytics(db: AsyncSession, period: str) -> RevenueAnalytics:
        now = datetime.now(timezone.utc)
        days_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
        days = days_map.get(period, 30)
        start = now - timedelta(days=days)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_week = now - timedelta(days=now.weekday())
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        def sum_revenue(since: datetime) -> float:
            return 0.0  # placeholder sync - computed below

        total_revenue_q = await db.execute(
            select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.status == "completed")
        )
        today_revenue_q = await db.execute(
            select(func.coalesce(func.sum(Payment.amount), 0)).where(
                Payment.status == "completed", Payment.created_at >= start_of_day
            )
        )
        week_revenue_q = await db.execute(
            select(func.coalesce(func.sum(Payment.amount), 0)).where(
                Payment.status == "completed", Payment.created_at >= start_of_week
            )
        )
        month_revenue_q = await db.execute(
            select(func.coalesce(func.sum(Payment.amount), 0)).where(
                Payment.status == "completed", Payment.created_at >= start_of_month
            )
        )
        total_rides_q = await db.execute(
            select(func.count()).select_from(Payment).where(Payment.status == "completed")
        )
        avg_fare_q = await db.execute(
            select(func.coalesce(func.avg(Payment.amount), 0)).where(Payment.status == "completed")
        )

        total_revenue = float(total_revenue_q.scalar() or 0)
        total_rides = int(total_rides_q.scalar() or 0)
        summary = RevenueSummary(
            total_revenue=total_revenue,
            today_revenue=float(today_revenue_q.scalar() or 0),
            week_revenue=float(week_revenue_q.scalar() or 0),
            month_revenue=float(month_revenue_q.scalar() or 0),
            total_rides=total_rides,
            average_fare=float(avg_fare_q.scalar() or 0),
            commission_earned=round(total_revenue * 0.15, 2),
        )

        daily: List[RevenueDataPoint] = []
        for i in range(days):
            day_start = (start + timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            day_rev = await db.execute(
                select(func.coalesce(func.sum(Payment.amount), 0)).where(
                    Payment.status == "completed",
                    Payment.created_at >= day_start,
                    Payment.created_at < day_end,
                )
            )
            day_rides = await db.execute(
                select(func.count()).select_from(Payment).where(
                    Payment.status == "completed",
                    Payment.created_at >= day_start,
                    Payment.created_at < day_end,
                )
            )
            rev = day_rev.scalar()
            rides_count = day_rides.scalar()
            daily.append(
                RevenueDataPoint(
                    date=day_start.strftime("%Y-%m-%d"),
                    revenue=float(rev or 0),
                    rides=int(rides_count or 0),
                )
            )

        monthly: List[RevenueDataPoint] = []
        for m in range(min(12, max(1, days // 30))):
            month_start = (now.replace(day=1) - timedelta(days=30 * m)).replace(
                day=1, hour=0, minute=0, second=0, microsecond=0
            )
            if m == 0:
                month_end = now
            else:
                month_end = (now.replace(day=1) - timedelta(days=30 * (m - 1))).replace(
                    day=1, hour=0, minute=0, second=0, microsecond=0
                )
            month_rev = await db.execute(
                select(func.coalesce(func.sum(Payment.amount), 0)).where(
                    Payment.status == "completed",
                    Payment.created_at >= month_start,
                    Payment.created_at < month_end,
                )
            )
            month_rides = await db.execute(
                select(func.count()).select_from(Payment).where(
                    Payment.status == "completed",
                    Payment.created_at >= month_start,
                    Payment.created_at < month_end,
                )
            )
            rev = month_rev.scalar()
            rides_count = month_rides.scalar()
            monthly.append(
                RevenueDataPoint(
                    date=month_start.strftime("%Y-%m"),
                    revenue=float(rev or 0),
                    rides=int(rides_count or 0),
                )
            )

        return RevenueAnalytics(summary=summary, daily=daily, monthly=list(reversed(monthly)))

    @staticmethod
    async def export_revenue_csv(db: AsyncSession, period: str) -> str:
        analytics = await AdminPanelService.revenue_analytics(db, period)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["date", "revenue", "rides"])
        for point in analytics.daily:
            writer.writerow([point.date, point.revenue, point.rides])
        return output.getvalue()

    @staticmethod
    def _broadcast_to_schema(item: BroadcastNotification) -> AdminBroadcastNotification:
        return AdminBroadcastNotification(
            id=str(item.id),
            title=item.title,
            message=item.message,
            target=item.target,
            status=item.status,
            scheduled_at=item.scheduled_at,
            sent_at=item.sent_at,
            recipient_count=item.recipient_count,
            created_at=item.created_at,
        )

    @staticmethod
    async def list_broadcasts(
        db: AsyncSession, page: int, page_size: int
    ) -> PaginatedResponse[AdminBroadcastNotification]:
        total = (await db.execute(select(func.count()).select_from(BroadcastNotification))).scalar() or 0
        result = await db.execute(
            select(BroadcastNotification)
            .order_by(BroadcastNotification.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = [AdminPanelService._broadcast_to_schema(n) for n in result.scalars().all()]
        return paginate(items, total, page, page_size)

    @staticmethod
    async def create_broadcast(db: AsyncSession, payload) -> AdminBroadcastNotification:
        status = "scheduled" if payload.scheduled_at else "draft"
        notification = BroadcastNotification(
            title=payload.title,
            message=payload.message,
            target=payload.target,
            target_ids=json.dumps(payload.target_ids) if payload.target_ids else None,
            status=status,
            scheduled_at=payload.scheduled_at,
        )
        db.add(notification)
        await db.flush()
        return AdminPanelService._broadcast_to_schema(notification)

    @staticmethod
    async def get_broadcast(db: AsyncSession, notification_id: int) -> AdminBroadcastNotification:
        result = await db.execute(
            select(BroadcastNotification).where(BroadcastNotification.id == notification_id)
        )
        item = result.scalar_one_or_none()
        if not item:
            raise NotFoundError("Notification not found")
        return AdminPanelService._broadcast_to_schema(item)

    @staticmethod
    async def send_broadcast(db: AsyncSession, notification_id: int) -> AdminBroadcastNotification:
        result = await db.execute(
            select(BroadcastNotification).where(BroadcastNotification.id == notification_id)
        )
        item = result.scalar_one_or_none()
        if not item:
            raise NotFoundError("Notification not found")
        if item.status == "sent":
            raise ValidationError("Notification already sent")

        if item.target in ("all_users", "specific_users"):
            count_q = await db.execute(select(func.count()).select_from(User).where(User.is_admin.is_(False)))
        else:
            count_q = await db.execute(select(func.count()).select_from(Driver))
        item.recipient_count = count_q.scalar() or 0
        item.status = "sent"
        item.sent_at = datetime.now(timezone.utc)
        await db.flush()
        return AdminPanelService._broadcast_to_schema(item)

    @staticmethod
    async def cancel_broadcast(db: AsyncSession, notification_id: int) -> AdminBroadcastNotification:
        result = await db.execute(
            select(BroadcastNotification).where(BroadcastNotification.id == notification_id)
        )
        item = result.scalar_one_or_none()
        if not item:
            raise NotFoundError("Notification not found")
        item.status = "draft"
        item.scheduled_at = None
        await db.flush()
        return AdminPanelService._broadcast_to_schema(item)

    @staticmethod
    async def delete_broadcast(db: AsyncSession, notification_id: int) -> None:
        result = await db.execute(
            select(BroadcastNotification).where(BroadcastNotification.id == notification_id)
        )
        item = result.scalar_one_or_none()
        if not item:
            raise NotFoundError("Notification not found")
        await db.delete(item)

    @staticmethod
    async def list_complaints(
        db: AsyncSession,
        page: int,
        page_size: int,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> PaginatedResponse[AdminComplaintItem]:
        query = select(Complaint, User).join(User, User.id == Complaint.user_id)
        if status:
            query = query.where(Complaint.status == status)
        if search:
            pattern = f"%{search}%"
            query = query.where(or_(Complaint.subject.ilike(pattern), Complaint.description.ilike(pattern)))

        total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar() or 0
        result = await db.execute(
            query.order_by(Complaint.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        )

        items = []
        for complaint, user in result.all():
            items.append(
                AdminComplaintItem(
                    id=str(complaint.id),
                    user_id=str(complaint.user_id),
                    user_name=user.full_name,
                    ride_id=complaint.reference_id if complaint.reference_type == "ride" else None,
                    subject=complaint.subject,
                    description=complaint.description,
                    status=complaint.status,
                    priority=getattr(complaint, "priority", "medium"),
                    assigned_to=None,
                    resolution=complaint.admin_response,
                    created_at=complaint.created_at,
                    updated_at=complaint.updated_at,
                )
            )
        return paginate(items, total, page, page_size)

    @staticmethod
    async def update_complaint(db: AsyncSession, complaint_id: int, payload) -> AdminComplaintItem:
        result = await db.execute(
            select(Complaint, User).join(User, User.id == Complaint.user_id).where(Complaint.id == complaint_id)
        )
        row = result.one_or_none()
        if not row:
            raise NotFoundError("Complaint not found")
        complaint, user = row

        if payload.status is not None:
            complaint.status = payload.status
        if payload.resolution is not None:
            complaint.admin_response = payload.resolution
        if hasattr(complaint, "priority") and payload.priority is not None:
            complaint.priority = payload.priority

        await db.flush()
        return AdminComplaintItem(
            id=str(complaint.id),
            user_id=str(complaint.user_id),
            user_name=user.full_name,
            ride_id=complaint.reference_id if complaint.reference_type == "ride" else None,
            subject=complaint.subject,
            description=complaint.description,
            status=complaint.status,
            priority=getattr(complaint, "priority", "medium"),
            assigned_to=payload.assigned_to,
            resolution=complaint.admin_response,
            created_at=complaint.created_at,
            updated_at=complaint.updated_at,
        )
