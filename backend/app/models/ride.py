from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.driver import Driver
    from app.models.vehicle import Vehicle
    from app.models.payment import Payment


class Ride(Base, TimestampMixin):
    __tablename__ = "rides"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    driver_id: Mapped[Optional[int]] = mapped_column(ForeignKey("drivers.id", ondelete="SET NULL"), nullable=True)
    vehicle_id: Mapped[Optional[int]] = mapped_column(ForeignKey("vehicles.id", ondelete="SET NULL"), nullable=True)

    ride_type: Mapped[str] = mapped_column(String(20), nullable=False)  # bike, auto, taxi
    status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False, index=True)
    # pending, searching, accepted, arrived, in_progress, completed, cancelled

    pickup_latitude: Mapped[float] = mapped_column(Float, nullable=False)
    pickup_longitude: Mapped[float] = mapped_column(Float, nullable=False)
    pickup_address: Mapped[str] = mapped_column(Text, nullable=False)
    dropoff_latitude: Mapped[float] = mapped_column(Float, nullable=False)
    dropoff_longitude: Mapped[float] = mapped_column(Float, nullable=False)
    dropoff_address: Mapped[str] = mapped_column(Text, nullable=False)

    estimated_distance_km: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    estimated_fare: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    actual_distance_km: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    actual_fare: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    accepted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    cancellation_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    otp_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="rides")
    driver: Mapped[Optional["Driver"]] = relationship("Driver", back_populates="rides")
    vehicle: Mapped[Optional["Vehicle"]] = relationship("Vehicle", back_populates="rides")
    payment: Mapped[Optional["Payment"]] = relationship(
        "Payment", back_populates="ride", uselist=False, cascade="all, delete-orphan"
    )
