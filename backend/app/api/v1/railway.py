from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

import redis.asyncio as aioredis

from app.core.database import get_db
from app.core.deps import get_current_active_user, get_redis
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.railway import (
    FavoriteTrainCreate,
    FavoriteTrainResponse,
    LiveStatusRequest,
    LiveStatusResponse,
    PNRStatusRequest,
    PNRStatusResponse,
    ScheduleRequest,
    ScheduleResponse,
    StationResponse,
    StationSearchRequest,
    TrainSearchRequest,
    TrainSearchResult,
)
from app.services.railway_service import RailwayService
from app.services.redis_cache import RedisCache


router = APIRouter(prefix="/railway", tags=["Railway"])


def get_railway_service(
    db: AsyncSession = Depends(get_db),
    redis_client: aioredis.Redis = Depends(get_redis),
) -> RailwayService:
    return RailwayService(db, RedisCache(redis_client))


@router.post("/trains/search", response_model=List[TrainSearchResult])
async def search_trains(
    payload: TrainSearchRequest,
    service: RailwayService = Depends(get_railway_service),
):
    results = await service.search_trains(payload.source, payload.destination, payload.date)
    return results


@router.post("/pnr/status", response_model=PNRStatusResponse)
async def pnr_status(
    payload: PNRStatusRequest,
    service: RailwayService = Depends(get_railway_service),
):
    result = await service.get_pnr_status(payload.pnr_number)
    return result


@router.post("/trains/live-status", response_model=LiveStatusResponse)
async def live_status(
    payload: LiveStatusRequest,
    service: RailwayService = Depends(get_railway_service),
):
    result = await service.get_live_status(payload.train_number, payload.date)
    return result


@router.get("/trains/{train_number}/live-status", response_model=LiveStatusResponse)
async def live_status_get(
    train_number: str,
    date: str = Query(None),
    service: RailwayService = Depends(get_railway_service),
):
    result = await service.get_live_status(train_number, date)
    return result


@router.post("/trains/schedule", response_model=ScheduleResponse)
async def train_schedule(
    payload: ScheduleRequest,
    service: RailwayService = Depends(get_railway_service),
):
    result = await service.get_schedule(payload.train_number)
    return result


@router.get("/trains/{train_number}/schedule", response_model=ScheduleResponse)
async def train_schedule_get(
    train_number: str,
    service: RailwayService = Depends(get_railway_service),
):
    result = await service.get_schedule(train_number)
    return result


@router.post("/stations/search", response_model=List[StationResponse])
async def search_stations(
    payload: StationSearchRequest,
    service: RailwayService = Depends(get_railway_service),
):
    results = await service.search_stations(payload.query)
    return results


@router.get("/stations/search", response_model=List[StationResponse])
async def search_stations_get(
    q: str = Query(..., min_length=2),
    service: RailwayService = Depends(get_railway_service),
):
    results = await service.search_stations(q)
    return results


@router.get("/stations/{station_code}", response_model=StationResponse)
async def get_station(
    station_code: str,
    service: RailwayService = Depends(get_railway_service),
):
    station = await service.get_station_by_code(station_code)
    return station


@router.get("/favorites", response_model=List[FavoriteTrainResponse])
async def list_favorites(
    current_user: User = Depends(get_current_active_user),
    service: RailwayService = Depends(get_railway_service),
):
    favorites = await service.get_favorite_trains(current_user.id)
    return favorites


@router.post("/favorites", response_model=FavoriteTrainResponse, status_code=201)
async def add_favorite(
    payload: FavoriteTrainCreate,
    current_user: User = Depends(get_current_active_user),
    service: RailwayService = Depends(get_railway_service),
):
    favorite = await service.add_favorite_train(
        current_user.id,
        payload.train_number,
        payload.train_name,
        payload.nickname,
    )
    return favorite


@router.delete("/favorites/{favorite_id}", response_model=MessageResponse)
async def remove_favorite(
    favorite_id: int,
    current_user: User = Depends(get_current_active_user),
    service: RailwayService = Depends(get_railway_service),
):
    await service.remove_favorite_train(current_user.id, favorite_id)
    return MessageResponse(message="Favorite train removed")
