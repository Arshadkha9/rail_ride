from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.driver import Driver
    from app.models.wallet import Wallet
    from app.models.ride import Ride
    from app.models.notification import Notification
    from app.models.railway import FavoriteTrain, TripHistory, Complaint


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
    mobile: Mapped[Optional[str]] = mapped_column(String(20), unique=True, index=True, nullable=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    driver: Mapped[Optional["Driver"]] = relationship(
        "Driver", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    wallet: Mapped[Optional["Wallet"]] = relationship(
        "Wallet", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    rides: Mapped[List["Ride"]] = relationship("Ride", back_populates="user", cascade="all, delete-orphan")
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )
    favorite_trains: Mapped[List["FavoriteTrain"]] = relationship(
        "FavoriteTrain", back_populates="user", cascade="all, delete-orphan"
    )
    trip_history: Mapped[List["TripHistory"]] = relationship(
        "TripHistory", back_populates="user", cascade="all, delete-orphan"
    )
    complaints: Mapped[List["Complaint"]] = relationship(
        "Complaint", back_populates="user", cascade="all, delete-orphan"
    )
