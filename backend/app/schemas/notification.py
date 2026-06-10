from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class NotificationResponse(BaseSchema):
    id: int
    user_id: int
    title: str
    message: str
    notification_type: str
    data: Optional[str] = None
    is_read: bool
    created_at: datetime


class NotificationCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    notification_type: str = Field(..., min_length=1, max_length=50)
    data: Optional[str] = None


class MarkReadRequest(BaseModel):
    notification_ids: List[int]
