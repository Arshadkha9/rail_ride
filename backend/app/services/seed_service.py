from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.user import User
from app.models.wallet import Wallet


async def seed_admin_user(db: AsyncSession) -> None:
    result = await db.execute(select(User).where(User.email == "admin@railride.com"))
    if result.scalar_one_or_none():
        return

    admin = User(
        full_name="RailRide Admin",
        email="admin@railride.com",
        mobile="+919999999999",
        password_hash=get_password_hash("Admin@123"),
        is_active=True,
        is_verified=True,
        is_admin=True,
    )
    db.add(admin)
    await db.flush()

    wallet = Wallet(user_id=admin.id, balance=0.0)
    db.add(wallet)
    await db.flush()
