from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema


class TrainSearchRequest(BaseModel):
    source: str = Field(..., min_length=2, max_length=10)
    destination: str = Field(..., min_length=2, max_length=10)
    date: Optional[str] = Field(None, description="YYYY-MM-DD")


class TrainResponse(BaseSchema):
    id: int
    train_number: str
    train_name: str
    train_type: str
    source_station_code: str
    destination_station_code: str
    departure_time: Optional[str] = None
    arrival_time: Optional[str] = None
    running_days: Optional[str] = None
    is_active: bool


class TrainSearchResult(BaseModel):
    train_number: str
    train_name: str
    train_type: str
    source: str
    destination: str
    departure_time: str
    arrival_time: str
    duration: str
    available_classes: List[str]
    fare: dict


class PNRStatusRequest(BaseModel):
    pnr_number: str = Field(..., min_length=10, max_length=10, pattern=r"^[0-9]{10}$")


class PassengerStatus(BaseModel):
    name: str
    booking_status: str
    current_status: str
    coach: str
    seat: str


class PNRStatusResponse(BaseModel):
    pnr_number: str
    train_number: str
    train_name: str
    from_station: str
    to_station: str
    journey_date: str
    class_code: str
    chart_prepared: bool
    passengers: List[PassengerStatus]


class LiveStatusRequest(BaseModel):
    train_number: str
    date: Optional[str] = None


class StationLiveStatus(BaseModel):
    station_code: str
    station_name: str
    scheduled_arrival: Optional[str] = None
    actual_arrival: Optional[str] = None
    scheduled_departure: Optional[str] = None
    actual_departure: Optional[str] = None
    delay_minutes: int = 0
    platform: Optional[str] = None


class LiveStatusResponse(BaseModel):
    train_number: str
    train_name: str
    current_station: Optional[str] = None
    last_updated: str
    stations: List[StationLiveStatus]


class ScheduleRequest(BaseModel):
    train_number: str


class ScheduleStop(BaseModel):
    station_code: str
    station_name: str
    arrival_time: Optional[str] = None
    departure_time: Optional[str] = None
    day: int
    distance_km: float
    halt_minutes: int


class ScheduleResponse(BaseModel):
    train_number: str
    train_name: str
    source: str
    destination: str
    running_days: str
    stops: List[ScheduleStop]


class StationResponse(BaseSchema):
    id: int
    station_code: str
    station_name: str
    city: str
    state: str
    zone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class StationSearchRequest(BaseModel):
    query: str = Field(..., min_length=2)


class FavoriteTrainCreate(BaseModel):
    train_number: str
    train_name: Optional[str] = None
    nickname: Optional[str] = None


class FavoriteTrainResponse(BaseSchema):
    id: int
    train_number: str
    train_name: Optional[str] = None
    nickname: Optional[str] = None
    created_at: datetime
