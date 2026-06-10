from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_admin_user
from app.models.user import User
from app.schemas.admin_panel import AdminLoginRequest, AdminLoginResponse, AdminUserResponse
from app.schemas.common import MessageResponse
from app.services.auth_service import AuthService


router = APIRouter(prefix="/admin/auth", tags=["Admin Auth"])


@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(
    payload: AdminLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await AuthService.authenticate_email(db, payload.email, payload.password)
    if not user.is_admin:
        from app.core.exceptions import ForbiddenError
        raise ForbiddenError("Admin access required")

    access_token, _refresh_token = await AuthService.create_tokens(db, user)
    return AdminLoginResponse(
        access_token=access_token,
        expires_in=settings.access_token_expire_minutes * 60,
        admin=AdminUserResponse(
            id=str(user.id),
            email=user.email or "",
            full_name=user.full_name,
        ),
    )


@router.get("/me", response_model=AdminUserResponse)
async def admin_me(admin_user: User = Depends(get_current_admin_user)):
    return AdminUserResponse(
        id=str(admin_user.id),
        email=admin_user.email or "",
        full_name=admin_user.full_name,
    )


@router.post("/logout", response_model=MessageResponse)
async def admin_logout(admin_user: User = Depends(get_current_admin_user)):
    return MessageResponse(message="Logged out successfully")


@router.post("/refresh", response_model=AdminLoginResponse)
async def admin_refresh(
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
):
    access_token, _refresh_token = await AuthService.create_tokens(db, admin_user)
    return AdminLoginResponse(
        access_token=access_token,
        expires_in=settings.access_token_expire_minutes * 60,
        admin=AdminUserResponse(
            id=str(admin_user.id),
            email=admin_user.email or "",
            full_name=admin_user.full_name,
        ),
    )
