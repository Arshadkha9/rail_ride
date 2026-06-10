import random
import string
from datetime import datetime, timedelta

from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ValidationError
from app.models.otp import OTP


class OTPService:
    @staticmethod
    def generate_otp() -> str:
        return "".join(random.choices(string.digits, k=settings.otp_length))

    @staticmethod
    async def create_otp(
        db: AsyncSession,
        identifier: str,
        purpose: str,
    ) -> str:
        await db.execute(
            update(OTP)
            .where(
                and_(
                    OTP.identifier == identifier,
                    OTP.purpose == purpose,
                    OTP.is_used == False,  # noqa: E712
                )
            )
            .values(is_used=True)
        )

        otp_code = OTPService.generate_otp()
        expires_at = datetime.utcnow() + timedelta(minutes=settings.otp_expire_minutes)

        otp_record = OTP(
            identifier=identifier,
            otp_code=otp_code,
            purpose=purpose,
            expires_at=expires_at,
        )
        db.add(otp_record)
        await db.flush()

        return otp_code

    @staticmethod
    async def verify_otp(
        db: AsyncSession,
        identifier: str,
        otp_code: str,
        purpose: str,
    ) -> bool:
        result = await db.execute(
            select(OTP).where(
                and_(
                    OTP.identifier == identifier,
                    OTP.purpose == purpose,
                    OTP.is_used == False,  # noqa: E712
                )
            ).order_by(OTP.created_at.desc())
        )
        otp_record = result.scalar_one_or_none()

        if otp_record is None:
            raise ValidationError("OTP not found or already used")

        if otp_record.expires_at < datetime.utcnow():
            raise ValidationError("OTP has expired")

        otp_record.attempts += 1
        if otp_record.attempts > 5:
            otp_record.is_used = True
            raise ValidationError("Maximum OTP attempts exceeded")

        if otp_record.otp_code != otp_code:
            await db.flush()
            raise ValidationError("Invalid OTP code")

        otp_record.is_used = True
        await db.flush()
        return True
