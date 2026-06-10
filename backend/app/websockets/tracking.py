import asyncio
import json
import logging
from typing import Dict, Optional, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import decode_token
from app.models.driver import Driver
from app.models.ride import Ride


logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.ride_connections: Dict[int, Set[WebSocket]] = {}
        self.driver_connections: Dict[int, WebSocket] = {}

    async def connect_ride(self, websocket: WebSocket, ride_id: int) -> None:
        await websocket.accept()
        if ride_id not in self.ride_connections:
            self.ride_connections[ride_id] = set()
        self.ride_connections[ride_id].add(websocket)
        logger.info("Client connected to ride %s tracking", ride_id)

    def disconnect_ride(self, websocket: WebSocket, ride_id: int) -> None:
        if ride_id in self.ride_connections:
            self.ride_connections[ride_id].discard(websocket)
            if not self.ride_connections[ride_id]:
                del self.ride_connections[ride_id]
        logger.info("Client disconnected from ride %s tracking", ride_id)

    async def connect_driver(self, websocket: WebSocket, driver_id: int) -> None:
        await websocket.accept()
        self.driver_connections[driver_id] = websocket
        logger.info("Driver %s connected for location updates", driver_id)

    def disconnect_driver(self, driver_id: int) -> None:
        if driver_id in self.driver_connections:
            del self.driver_connections[driver_id]
        logger.info("Driver %s disconnected", driver_id)

    async def broadcast_to_ride(self, ride_id: int, message: dict) -> None:
        if ride_id not in self.ride_connections:
            return

        disconnected = set()
        for websocket in self.ride_connections[ride_id]:
            try:
                await websocket.send_json(message)
            except Exception:
                disconnected.add(websocket)

        for ws in disconnected:
            self.ride_connections[ride_id].discard(ws)


manager = ConnectionManager()


async def authenticate_websocket(token: str) -> Optional[int]:
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        return None
    return int(payload.get("sub"))


@router.websocket("/ws/tracking/{ride_id}")
async def ride_tracking_websocket(websocket: WebSocket, ride_id: int, token: str = None):
    if not token:
        await websocket.close(code=4001, reason="Authentication required")
        return

    user_id = await authenticate_websocket(token)
    if not user_id:
        await websocket.close(code=4001, reason="Invalid token")
        return

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Ride).where(Ride.id == ride_id, Ride.user_id == user_id)
        )
        ride = result.scalar_one_or_none()
        if not ride:
            await websocket.close(code=4004, reason="Ride not found")
            return

    await manager.connect_ride(websocket, ride_id)

    try:
        while True:
            async with AsyncSessionLocal() as db:
                result = await db.execute(select(Ride).where(Ride.id == ride_id))
                ride = result.scalar_one_or_none()

                if not ride:
                    await websocket.send_json({"error": "Ride not found"})
                    break

                driver_lat = None
                driver_lon = None

                if ride.driver_id:
                    driver_result = await db.execute(
                        select(Driver).where(Driver.id == ride.driver_id)
                    )
                    driver = driver_result.scalar_one_or_none()
                    if driver:
                        driver_lat = driver.current_latitude
                        driver_lon = driver.current_longitude

                await websocket.send_json({
                    "type": "location_update",
                    "ride_id": ride_id,
                    "status": ride.status,
                    "driver_latitude": driver_lat,
                    "driver_longitude": driver_lon,
                    "pickup_latitude": ride.pickup_latitude,
                    "pickup_longitude": ride.pickup_longitude,
                    "dropoff_latitude": ride.dropoff_latitude,
                    "dropoff_longitude": ride.dropoff_longitude,
                })

                if ride.status in ("completed", "cancelled"):
                    await websocket.send_json({
                        "type": "ride_ended",
                        "ride_id": ride_id,
                        "status": ride.status,
                    })
                    break

            await asyncio.sleep(3)

    except WebSocketDisconnect:
        manager.disconnect_ride(websocket, ride_id)
    except Exception as exc:
        logger.error("WebSocket error for ride %s: %s", ride_id, exc)
        manager.disconnect_ride(websocket, ride_id)


@router.websocket("/ws/driver/{driver_id}")
async def driver_location_websocket(websocket: WebSocket, driver_id: int, token: str = None):
    if not token:
        await websocket.close(code=4001, reason="Authentication required")
        return

    user_id = await authenticate_websocket(token)
    if not user_id:
        await websocket.close(code=4001, reason="Invalid token")
        return

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Driver).where(Driver.id == driver_id, Driver.user_id == user_id)
        )
        driver = result.scalar_one_or_none()
        if not driver:
            await websocket.close(code=4004, reason="Driver not found")
            return

    await manager.connect_driver(websocket, driver_id)

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "location_update":
                latitude = message.get("latitude")
                longitude = message.get("longitude")

                if latitude is not None and longitude is not None:
                    async with AsyncSessionLocal() as db:
                        result = await db.execute(
                            select(Driver).where(Driver.id == driver_id)
                        )
                        driver = result.scalar_one_or_none()
                        if driver:
                            driver.current_latitude = latitude
                            driver.current_longitude = longitude
                            await db.commit()

                        ride_result = await db.execute(
                            select(Ride).where(
                                Ride.driver_id == driver_id,
                                Ride.status.in_(["accepted", "arrived", "in_progress"]),
                            )
                        )
                        active_rides = ride_result.scalars().all()

                        for ride in active_rides:
                            await manager.broadcast_to_ride(ride.id, {
                                "type": "location_update",
                                "ride_id": ride.id,
                                "status": ride.status,
                                "driver_latitude": latitude,
                                "driver_longitude": longitude,
                            })

                    await websocket.send_json({
                        "type": "ack",
                        "message": "Location updated",
                    })

    except WebSocketDisconnect:
        manager.disconnect_driver(driver_id)
    except Exception as exc:
        logger.error("Driver WebSocket error for driver %s: %s", driver_id, exc)
        manager.disconnect_driver(driver_id)
