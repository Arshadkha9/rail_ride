import math
import random
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import NotFoundError, ValidationError
from app.models.driver import Driver
from app.models.payment import Payment
from app.models.ride import Ride
from app.models.railway import TripHistory
from app.models.user import User
from app.models.vehicle import Vehicle
from app.services.auth_service import AuthService
from app.services.notification_service import NotificationService
from app.services.wallet_service import WalletService


class RideService:
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        radius = 6371.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return round(radius * c, 2)

    @classmethod
    def estimate_fare(cls, ride_type: str, distance_km: float) -> Tuple[float, dict]:
        fare_config = {
            "bike": (settings.base_fare_bike, settings.fare_bike_per_km),
            "auto": (settings.base_fare_auto, settings.fare_auto_per_km),
            "taxi": (settings.base_fare_taxi, settings.fare_taxi_per_km),
        }

        if ride_type not in fare_config:
            raise ValidationError("Invalid ride type")

        base_fare, per_km = fare_config[ride_type]
        distance_fare = distance_km * per_km
        total = round(base_fare + distance_fare, 2)

        breakdown = {
            "base_fare": base_fare,
            "distance_km": distance_km,
            "per_km_rate": per_km,
            "distance_fare": round(distance_fare, 2),
            "total": total,
        }
        return total, breakdown

    @classmethod
    async def estimate(
        cls,
        ride_type: str,
        pickup_lat: float,
        pickup_lon: float,
        dropoff_lat: float,
        dropoff_lon: float,
    ) -> dict:
        distance = cls.haversine_distance(pickup_lat, pickup_lon, dropoff_lat, dropoff_lon)
        distance = max(distance, 1.0)
        duration_minutes = int(distance * 3)
        fare, breakdown = cls.estimate_fare(ride_type, distance)

        return {
            "ride_type": ride_type,
            "estimated_distance_km": distance,
            "estimated_duration_minutes": duration_minutes,
            "estimated_fare": fare,
            "currency": "INR",
            "breakdown": breakdown,
        }

    @staticmethod
    async def find_nearby_driver(
        db: AsyncSession,
        ride_type: str,
        latitude: float,
        longitude: float,
    ) -> Optional[Tuple[Driver, Vehicle]]:
        result = await db.execute(
            select(Driver, Vehicle)
            .join(Vehicle, Vehicle.driver_id == Driver.id)
            .where(
                Driver.is_available == True,  # noqa: E712
                Driver.is_verified == True,  # noqa: E712
                Vehicle.vehicle_type == ride_type,
                Vehicle.is_active == True,  # noqa: E712
            )
        )
        drivers = result.all()

        if not drivers:
            return None

        driver, vehicle = random.choice(drivers)
        return driver, vehicle

    @classmethod
    async def book_ride(
        cls,
        db: AsyncSession,
        user: User,
        ride_type: str,
        pickup_lat: float,
        pickup_lon: float,
        pickup_address: str,
        dropoff_lat: float,
        dropoff_lon: float,
        dropoff_address: str,
        payment_method: str = "wallet",
        scheduled_at: Optional[datetime] = None,
    ) -> Ride:
        estimate = await cls.estimate(ride_type, pickup_lat, pickup_lon, dropoff_lat, dropoff_lon)

        ride = Ride(
            user_id=user.id,
            ride_type=ride_type,
            status="searching",
            pickup_latitude=pickup_lat,
            pickup_longitude=pickup_lon,
            pickup_address=pickup_address,
            dropoff_latitude=dropoff_lat,
            dropoff_longitude=dropoff_lon,
            dropoff_address=dropoff_address,
            estimated_distance_km=estimate["estimated_distance_km"],
            estimated_fare=estimate["estimated_fare"],
            scheduled_at=scheduled_at,
            otp_code=AuthService.generate_ride_otp(),
        )
        db.add(ride)
        await db.flush()

        driver_match = await cls.find_nearby_driver(db, ride_type, pickup_lat, pickup_lon)
        if driver_match:
            driver, vehicle = driver_match
            ride.driver_id = driver.id
            ride.vehicle_id = vehicle.id
            ride.status = "accepted"
            ride.accepted_at = datetime.utcnow()
            driver.is_available = False
            driver.current_latitude = pickup_lat + random.uniform(-0.01, 0.01)
            driver.current_longitude = pickup_lon + random.uniform(-0.01, 0.01)

        payment = Payment(
            ride_id=ride.id,
            user_id=user.id,
            amount=estimate["estimated_fare"],
            payment_method=payment_method,
            status="pending",
        )
        db.add(payment)
        await db.flush()

        trip = TripHistory(
            user_id=user.id,
            trip_type="ride",
            reference_id=str(ride.id),
            title=f"{ride_type.title()} ride",
            description=f"{pickup_address} to {dropoff_address}",
            status=ride.status,
            amount=estimate["estimated_fare"],
            trip_date=datetime.utcnow(),
        )
        db.add(trip)

        await NotificationService.create_notification(
            db,
            user_id=user.id,
            title="Ride Booked",
            message=f"Your {ride_type} ride has been booked. Status: {ride.status}",
            notification_type="ride_booked",
            data=f'{{"ride_id": {ride.id}}}',
        )

        await db.flush()
        return ride

    @staticmethod
    async def get_ride(db: AsyncSession, ride_id: int, user_id: int) -> Ride:
        result = await db.execute(
            select(Ride).where(Ride.id == ride_id, Ride.user_id == user_id)
        )
        ride = result.scalar_one_or_none()
        if not ride:
            raise NotFoundError("Ride not found")
        return ride

    @staticmethod
    async def get_user_rides(
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Ride]:
        result = await db.execute(
            select(Ride)
            .where(Ride.user_id == user_id)
            .order_by(Ride.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def cancel_ride(db: AsyncSession, ride: Ride, reason: str) -> Ride:
        if ride.status in ("completed", "cancelled"):
            raise ValidationError(f"Cannot cancel ride with status: {ride.status}")

        ride.status = "cancelled"
        ride.cancelled_at = datetime.utcnow()
        ride.cancellation_reason = reason

        if ride.driver_id:
            driver_result = await db.execute(select(Driver).where(Driver.id == ride.driver_id))
            driver = driver_result.scalar_one_or_none()
            if driver:
                driver.is_available = True

        await db.flush()
        return ride

    @staticmethod
    async def complete_ride(db: AsyncSession, ride: Ride) -> Ride:
        ride.status = "completed"
        ride.completed_at = datetime.utcnow()
        ride.actual_fare = ride.estimated_fare
        ride.actual_distance_km = ride.estimated_distance_km

        if ride.driver_id:
            driver_result = await db.execute(select(Driver).where(Driver.id == ride.driver_id))
            driver = driver_result.scalar_one_or_none()
            if driver:
                driver.is_available = True
                driver.total_rides += 1

        payment_result = await db.execute(select(Payment).where(Payment.ride_id == ride.id))
        payment = payment_result.scalar_one_or_none()
        if payment:
            if payment.payment_method == "wallet":
                await WalletService.debit_wallet(
                    db,
                    ride.user_id,
                    payment.amount,
                    f"Payment for ride #{ride.id}",
                    f"ride_{ride.id}",
                )
            payment.status = "completed"
            payment.transaction_id = f"TXN{ride.id}{int(datetime.utcnow().timestamp())}"

        await db.flush()
        return ride

    @staticmethod
    async def rate_ride(db: AsyncSession, ride: Ride, rating: int, feedback: Optional[str] = None) -> Ride:
        if ride.status != "completed":
            raise ValidationError("Can only rate completed rides")

        ride.rating = rating
        ride.feedback = feedback

        if ride.driver_id:
            driver_result = await db.execute(select(Driver).where(Driver.id == ride.driver_id))
            driver = driver_result.scalar_one_or_none()
            if driver:
                total = driver.total_rides or 1
                driver.rating = round(((driver.rating * (total - 1)) + rating) / total, 2)

        await db.flush()
        return ride

    @staticmethod
    async def get_tracking_info(db: AsyncSession, ride: Ride) -> dict:
        driver_lat = None
        driver_lon = None

        if ride.driver_id:
            driver_result = await db.execute(select(Driver).where(Driver.id == ride.driver_id))
            driver = driver_result.scalar_one_or_none()
            if driver:
                driver_lat = driver.current_latitude
                driver_lon = driver.current_longitude

        eta = None
        if driver_lat and driver_lon:
            distance = RideService.haversine_distance(
                driver_lat, driver_lon,
                ride.pickup_latitude, ride.pickup_longitude,
            )
            eta = max(int(distance * 3), 2)

        return {
            "ride_id": ride.id,
            "status": ride.status,
            "driver_latitude": driver_lat,
            "driver_longitude": driver_lon,
            "pickup_latitude": ride.pickup_latitude,
            "pickup_longitude": ride.pickup_longitude,
            "dropoff_latitude": ride.dropoff_latitude,
            "dropoff_longitude": ride.dropoff_longitude,
            "estimated_arrival_minutes": eta,
        }

    @staticmethod
    async def update_driver_location(
        db: AsyncSession,
        driver_id: int,
        latitude: float,
        longitude: float,
    ) -> Driver:
        result = await db.execute(select(Driver).where(Driver.id == driver_id))
        driver = result.scalar_one_or_none()
        if not driver:
            raise NotFoundError("Driver not found")

        driver.current_latitude = latitude
        driver.current_longitude = longitude
        await db.flush()
        return driver
