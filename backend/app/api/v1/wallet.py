from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.wallet import (
    AddMoneyRequest,
    PaymentInitiateResponse,
    UPIPaymentRequest,
    WalletResponse,
    WalletTransactionResponse,
)
from app.services.wallet_service import WalletService


router = APIRouter(prefix="/wallet", tags=["Wallet"])


@router.get("/balance", response_model=WalletResponse)
async def get_balance(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    wallet = await WalletService.get_balance(db, current_user.id)
    return wallet


@router.post("/add-money", response_model=WalletTransactionResponse)
async def add_money(
    payload: AddMoneyRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    transaction = await WalletService.add_money(
        db,
        current_user.id,
        payload.amount,
        payload.payment_method,
    )
    return transaction


@router.post("/upi/initiate", response_model=PaymentInitiateResponse)
async def initiate_upi_payment(
    payload: UPIPaymentRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await WalletService.initiate_upi_payment(
        db,
        current_user.id,
        payload.amount,
        payload.upi_id,
    )
    return result


@router.post("/upi/confirm/{transaction_id}", response_model=WalletTransactionResponse)
async def confirm_upi_payment(
    transaction_id: str,
    amount: float = Query(..., gt=0),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    transaction = await WalletService.confirm_upi_payment(
        db,
        current_user.id,
        transaction_id,
        amount,
    )
    return transaction


@router.get("/transactions", response_model=List[WalletTransactionResponse])
async def list_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    transactions = await WalletService.get_transactions(db, current_user.id, skip, limit)
    return transactions


@router.get("/transactions/{reference_id}", response_model=WalletTransactionResponse)
async def get_transaction(
    reference_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    transaction = await WalletService.get_transaction_by_reference(
        db, current_user.id, reference_id
    )
    return transaction
