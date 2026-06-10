import secrets
from datetime import timedelta
from typing import Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ConflictError, UnauthorizedError, ValidationError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.models.wallet import Wallet
from app.services.otp_service import OTPService


class AuthService:
    @staticmethod
    async def register_user(
        db: AsyncSession,
        full_name: str,
        email: Optional[str] = None,
        mobile: Optional[str] = None,
        password: Optional[str] = None,
    ) -> User:
        if not email and not mobile:
            raise ValidationError("Email or mobile is required")

        if email:
            existing = await db.execute(select(User).where(User.email == email))
            if existing.scalar_one_or_none():
                raise ConflictError("Email already registered")

        if mobile:
            existing = await db.execute(select(User).where(User.mobile == mobile))
            if existing.scalar_one_or_none():
                raise ConflictError("Mobile already registered")

        user = User(
            full_name=full_name,
            email=email,
            mobile=mobile,
            password_hash=get_password_hash(password) if password else None,
            is_verified=False,
        )
        db.add(user)
        await db.flush()

        wallet = Wallet(user_id=user.id, balance=0.0)
        db.add(wallet)
        await db.flush()

        return user

    @staticmethod
    async def authenticate_email(
        db: AsyncSession,
        email: str,
        password: str,
    ) -> User:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if user is None or not user.password_hash:
            raise UnauthorizedError("Invalid email or password")

        if not verify_password(password, user.password_hash):
            raise UnauthorizedError("Invalid email or password")

        if not user.is_active:
            raise UnauthorizedError("Account is deactivated")

        return user

    @staticmethod
    async def get_or_create_mobile_user(
        db: AsyncSession,
        mobile: str,
        full_name: Optional[str] = None,
    ) -> User:
        result = await db.execute(select(User).where(User.mobile == mobile))
        user = result.scalar_one_or_none()

        if user:
            return user

        user = User(
            full_name=full_name or f"User {mobile[-4:]}",
            mobile=mobile,
            is_verified=True,
        )
        db.add(user)
        await db.flush()

        wallet = Wallet(user_id=user.id, balance=0.0)
        db.add(wallet)
        await db.flush()

        return user

    @staticmethod
    async def create_tokens(db: AsyncSession, user: User) -> Tuple[str, str]:
        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)

        user.refresh_token = refresh_token
        await db.flush()

        return access_token, refresh_token

    @staticmethod
    async def refresh_access_token(db: AsyncSession, refresh_token: str) -> Tuple[str, str]:
        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid refresh token")

        user_id = payload.get("sub")
        result = await db.execute(select(User).where(User.id == int(user_id)))
        user = result.scalar_one_or_none()

        if user is None or not user.is_active:
            raise UnauthorizedError("User not found or inactive")

        if user.refresh_token != refresh_token:
            raise UnauthorizedError("Refresh token revoked")

        access_token = create_access_token(subject=user.id)
        new_refresh_token = create_refresh_token(subject=user.id)
        user.refresh_token = new_refresh_token
        await db.flush()

        return access_token, new_refresh_token

    @staticmethod
    async def reset_password(
        db: AsyncSession,
        email: str,
        otp_code: str,
        new_password: str,
    ) -> None:
        await OTPService.verify_otp(db, email, otp_code, "forgot_password")

        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if user is None:
            raise ValidationError("User not found")

        user.password_hash = get_password_hash(new_password)
        await db.flush()

    @staticmethod
    async def change_password(
        db: AsyncSession,
        user: User,
        current_password: str,
        new_password: str,
    ) -> None:
        if not user.password_hash or not verify_password(current_password, user.password_hash):
            raise UnauthorizedError("Current password is incorrect")

        user.password_hash = get_password_hash(new_password)
        await db.flush()

    @staticmethod
    async def get_user_profile(db: AsyncSession, user: User) -> dict:
        from app.models.ride import Ride
        from app.models.railway import TripHistory

        wallet_result = await db.execute(select(Wallet).where(Wallet.user_id == user.id))
        wallet = wallet_result.scalar_one_or_none()

        rides_count = await db.execute(
            select(func.count()).select_from(Ride).where(Ride.user_id == user.id)
        )
        trips_count = await db.execute(
            select(func.count()).select_from(TripHistory).where(TripHistory.user_id == user.id)
        )

        return {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "mobile": user.mobile,
            "avatar_url": user.avatar_url,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "is_admin": user.is_admin,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "wallet_balance": wallet.balance if wallet else 0.0,
            "total_rides": rides_count.scalar() or 0,
            "total_trips": trips_count.scalar() or 0,
        }

    @staticmethod
    def generate_ride_otp() -> str:
        return str(secrets.randbelow(9000) + 1000)
