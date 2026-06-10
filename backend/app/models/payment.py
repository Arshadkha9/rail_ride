from typing import TYPE_CHECKING, Optional

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.ride import Ride
    from app.models.user import User


class Payment(Base, TimestampMixin):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ride_id: Mapped[int] = mapped_column(ForeignKey("rides.id", ondelete="CASCADE"), unique=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    payment_method: Mapped[str] = mapped_column(String(30), nullable=False)  # wallet, upi, card, cash
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)  # pending, completed, failed, refunded
    transaction_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)
    gateway_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    ride: Mapped["Ride"] = relationship("Ride", back_populates="payment")
