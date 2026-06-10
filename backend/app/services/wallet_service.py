import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.models.wallet import Wallet, WalletTransaction


class WalletService:
    @staticmethod
    async def get_or_create_wallet(db: AsyncSession, user_id: int) -> Wallet:
        result = await db.execute(select(Wallet).where(Wallet.user_id == user_id))
        wallet = result.scalar_one_or_none()

        if not wallet:
            wallet = Wallet(user_id=user_id, balance=0.0)
            db.add(wallet)
            await db.flush()

        return wallet

    @staticmethod
    async def get_balance(db: AsyncSession, user_id: int) -> Wallet:
        return await WalletService.get_or_create_wallet(db, user_id)

    @staticmethod
    async def add_money(
        db: AsyncSession,
        user_id: int,
        amount: float,
        payment_method: str,
        description: Optional[str] = None,
    ) -> WalletTransaction:
        wallet = await WalletService.get_or_create_wallet(db, user_id)

        if not wallet.is_active:
            raise ValidationError("Wallet is deactivated")

        reference_id = f"ADD_{uuid.uuid4().hex[:12].upper()}"
        new_balance = round(wallet.balance + amount, 2)

        transaction = WalletTransaction(
            wallet_id=wallet.id,
            transaction_type="credit",
            amount=amount,
            balance_after=new_balance,
            description=description or f"Added money via {payment_method}",
            reference_id=reference_id,
            payment_method=payment_method,
            status="completed",
        )

        wallet.balance = new_balance
        db.add(transaction)
        await db.flush()

        return transaction

    @staticmethod
    async def initiate_upi_payment(
        db: AsyncSession,
        user_id: int,
        amount: float,
        upi_id: str,
    ) -> dict:
        reference_id = f"UPI_{uuid.uuid4().hex[:12].upper()}"

        return {
            "transaction_id": reference_id,
            "amount": amount,
            "payment_method": "upi",
            "status": "pending",
            "payment_url": None,
            "upi_deep_link": f"upi://pay?pa=railride@upi&pn=RailRide&am={amount}&tn=Wallet+Topup&tr={reference_id}",
        }

    @staticmethod
    async def confirm_upi_payment(
        db: AsyncSession,
        user_id: int,
        transaction_id: str,
        amount: float,
    ) -> WalletTransaction:
        return await WalletService.add_money(
            db,
            user_id,
            amount,
            "upi",
            f"UPI payment confirmed - {transaction_id}",
        )

    @staticmethod
    async def debit_wallet(
        db: AsyncSession,
        user_id: int,
        amount: float,
        description: str,
        reference_id: str,
    ) -> WalletTransaction:
        wallet = await WalletService.get_or_create_wallet(db, user_id)

        if wallet.balance < amount:
            raise ValidationError("Insufficient wallet balance")

        new_balance = round(wallet.balance - amount, 2)

        transaction = WalletTransaction(
            wallet_id=wallet.id,
            transaction_type="debit",
            amount=amount,
            balance_after=new_balance,
            description=description,
            reference_id=reference_id,
            payment_method="wallet",
            status="completed",
        )

        wallet.balance = new_balance
        db.add(transaction)
        await db.flush()

        return transaction

    @staticmethod
    async def get_transactions(
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> List[WalletTransaction]:
        wallet = await WalletService.get_or_create_wallet(db, user_id)

        result = await db.execute(
            select(WalletTransaction)
            .where(WalletTransaction.wallet_id == wallet.id)
            .order_by(WalletTransaction.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_transaction_by_reference(
        db: AsyncSession,
        user_id: int,
        reference_id: str,
    ) -> WalletTransaction:
        wallet = await WalletService.get_or_create_wallet(db, user_id)

        result = await db.execute(
            select(WalletTransaction).where(
                WalletTransaction.wallet_id == wallet.id,
                WalletTransaction.reference_id == reference_id,
            )
        )
        transaction = result.scalar_one_or_none()
        if not transaction:
            raise NotFoundError("Transaction not found")
        return transaction
