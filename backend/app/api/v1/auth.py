from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.core.exceptions import ValidationError
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    EmailLoginRequest,
    ForgotPasswordRequest,
    MobileLoginRequest,
    OTPRequest,
    OTPVerifyRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from app.schemas.common import MessageResponse
from app.schemas.user import ProfileResponse, UserResponse, UserUpdate
from app.services.auth_service import AuthService
from app.services.otp_service import OTPService


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await AuthService.register_user(
        db,
        full_name=payload.full_name,
        email=payload.email,
        mobile=payload.mobile,
        password=payload.password,
    )
    return user


@router.post("/login/email", response_model=TokenResponse)
async def login_email(
    payload: EmailLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await AuthService.authenticate_email(db, payload.email, payload.password)
    access_token, refresh_token = await AuthService.create_tokens(db, user)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/login/mobile", response_model=MessageResponse)
async def login_mobile_request_otp(
    payload: MobileLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    otp_code = await OTPService.create_otp(db, payload.mobile, "login")
    return MessageResponse(
        message=f"OTP sent to {payload.mobile}. (Dev OTP: {otp_code})",
    )


@router.post("/otp/send", response_model=MessageResponse)
async def send_otp(
    payload: OTPRequest,
    db: AsyncSession = Depends(get_db),
):
    otp_code = await OTPService.create_otp(db, payload.identifier, payload.purpose)
    return MessageResponse(
        message=f"OTP sent to {payload.identifier}. (Dev OTP: {otp_code})",
    )


@router.post("/otp/verify", response_model=TokenResponse)
async def verify_otp(
    payload: OTPVerifyRequest,
    db: AsyncSession = Depends(get_db),
):
    await OTPService.verify_otp(db, payload.identifier, payload.otp_code, payload.purpose)

    if payload.purpose == "login":
        user = await AuthService.get_or_create_mobile_user(db, payload.identifier)
    elif payload.purpose == "register":
        user = await AuthService.get_or_create_mobile_user(db, payload.identifier)
        user.is_verified = True
    elif payload.purpose == "forgot_password":
        raise ValidationError("Use /auth/reset-password endpoint for password reset")
    else:
        raise ValidationError("Invalid OTP purpose")

    access_token, refresh_token = await AuthService.create_tokens(db, user)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    payload: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    access_token, refresh_token = await AuthService.refresh_access_token(db, payload.refresh_token)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    payload: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    otp_code = await OTPService.create_otp(db, payload.email, "forgot_password")
    return MessageResponse(
        message=f"Password reset OTP sent to {payload.email}. (Dev OTP: {otp_code})",
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    payload: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    await AuthService.reset_password(db, payload.email, payload.otp_code, payload.new_password)
    return MessageResponse(message="Password reset successful")


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await AuthService.get_user_profile(db, current_user)
    return ProfileResponse(**profile)


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    payload: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    await db.flush()
    return current_user


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    payload: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await AuthService.change_password(
        db, current_user, payload.current_password, payload.new_password
    )
    return MessageResponse(message="Password changed successfully")


@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    current_user.refresh_token = None
    await db.flush()
    return MessageResponse(message="Logged out successfully")
