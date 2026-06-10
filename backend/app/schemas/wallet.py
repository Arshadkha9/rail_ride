from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class WalletResponse(BaseSchema):
    id: int
    user_id: int
    balance: float
    currency: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class AddMoneyRequest(BaseModel):
    amount: float = Field(..., gt=0, le=50000)
    payment_method: str = Field(..., pattern=r"^(upi|card|netbanking)$")


class UPIPaymentRequest(BaseModel):
    amount: float = Field(..., gt=0, le=50000)
    upi_id: str = Field(..., min_length=5, max_length=100, pattern=r"^[\w.\-]+@[\w]+$")


class WalletTransactionResponse(BaseSchema):
    id: int
    wallet_id: int
    transaction_type: str
    amount: float
    balance_after: float
    description: str
    reference_id: str
    payment_method: Optional[str] = None
    status: str
    created_at: datetime


class PaymentInitiateResponse(BaseModel):
    transaction_id: str
    amount: float
    payment_method: str
    status: str
    payment_url: Optional[str] = None
    upi_deep_link: Optional[str] = None
