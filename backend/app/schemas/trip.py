from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class TripHistoryResponse(BaseSchema):
    id: int
    user_id: int
    trip_type: str
    reference_id: str
    title: str
    description: Optional[str] = None
    status: str
    amount: Optional[float] = None
    trip_date: datetime
    created_at: datetime


class ComplaintCreate(BaseModel):
    category: str = Field(..., min_length=2, max_length=50)
    subject: str = Field(..., min_length=5, max_length=255)
    description: str = Field(..., min_length=10)
    reference_type: Optional[str] = None
    reference_id: Optional[str] = None


class ComplaintResponse(BaseSchema):
    id: int
    user_id: int
    category: str
    subject: str
    description: str
    status: str
    reference_type: Optional[str] = None
    reference_id: Optional[str] = None
    admin_response: Optional[str] = None
    created_at: datetime
    updated_at: datetime
