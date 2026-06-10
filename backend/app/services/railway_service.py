import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.railway import FavoriteTrain, Station, Train
from app.services.redis_cache import RedisCache


MOCK_TRAINS = [
    {
        "train_number": "12951",
        "train_name": "Rajdhani Express",
        "train_type": "Rajdhani",
        "source": "NDLS",
        "destination": "BCT",
        "departure_time": "16:55",
        "arrival_time": "08:35",
        "duration": "15h 40m",
        "available_classes": ["1A", "2A", "3A"],
        "fare": {"1A": 4500, "2A": 2800, "3A": 1800},
    },
    {
        "train_number": "12301",
        "train_name": "Howrah Rajdhani",
        "train_type": "Rajdhani",
        "source": "NDLS",
        "destination": "HWH",
        "departure_time": "16:55",
        "arrival_time": "10:00",
        "duration": "17h 05m",
        "available_classes": ["1A", "2A", "3A"],
        "fare": {"1A": 4200, "2A": 2600, "3A": 1700},
    },
    {
        "train_number": "12009",
        "train_name": "Shatabdi Express",
        "train_type": "Shatabdi",
        "source": "NDLS",
        "destination": "BPL",
        "departure_time": "06:00",
        "arrival_time": "14:30",
        "duration": "8h 30m",
        "available_classes": ["CC", "EC"],
        "fare": {"CC": 1200, "EC": 1800},
    },
    {
        "train_number": "12627",
        "train_name": "Karnataka Express",
        "train_type": "Superfast",
        "source": "NDLS",
        "destination": "SBC",
        "departure_time": "20:30",
        "arrival_time": "06:40",
        "duration": "34h 10m",
        "available_classes": ["SL", "3A", "2A"],
        "fare": {"SL": 800, "3A": 1500, "2A": 2200},
    },
]

MOCK_STATIONS = [
    {"station_code": "NDLS", "station_name": "New Delhi", "city": "Delhi", "state": "Delhi", "zone": "NR"},
    {"station_code": "BCT", "station_name": "Mumbai Central", "city": "Mumbai", "state": "Maharashtra", "zone": "WR"},
    {"station_code": "HWH", "station_name": "Howrah Junction", "city": "Kolkata", "state": "West Bengal", "zone": "ER"},
    {"station_code": "SBC", "station_name": "Bangalore City", "city": "Bangalore", "state": "Karnataka", "zone": "SWR"},
    {"station_code": "BPL", "station_name": "Bhopal Junction", "city": "Bhopal", "state": "Madhya Pradesh", "zone": "WCR"},
    {"station_code": "CNB", "station_name": "Kanpur Central", "city": "Kanpur", "state": "Uttar Pradesh", "zone": "NCR"},
    {"station_code": "AGC", "station_name": "Agra Cantt", "city": "Agra", "state": "Uttar Pradesh", "zone": "NCR"},
    {"station_code": "JP", "station_name": "Jaipur Junction", "city": "Jaipur", "state": "Rajasthan", "zone": "NWR"},
]


class RailwayService:
    """Mock railway API integration with Redis caching."""

    def __init__(self, db: AsyncSession, cache: Optional[RedisCache] = None):
        self.db = db
        self.cache = cache

    async def search_trains(
        self,
        source: str,
        destination: str,
        date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        cache_key = None
        if self.cache:
            cache_key = self.cache.train_search_key(source, destination, date)
            cached = await self.cache.get(cache_key)
            if cached:
                return cached

        source_upper = source.upper()
        dest_upper = destination.upper()

        results = []
        for train in MOCK_TRAINS:
            if train["source"] == source_upper and train["destination"] == dest_upper:
                results.append(train)

        if not results:
            results = [
                {
                    **train,
                    "source": source_upper,
                    "destination": dest_upper,
                }
                for train in MOCK_TRAINS[:2]
            ]

        if self.cache and cache_key:
            await self.cache.set(cache_key, results)

        return results

    async def get_pnr_status(self, pnr_number: str) -> Dict[str, Any]:
        if self.cache:
            cache_key = self.cache.pnr_key(pnr_number)
            cached = await self.cache.get(cache_key)
            if cached:
                return cached

        seed = int(hashlib.md5(pnr_number.encode()).hexdigest(), 16)
        train_idx = seed % len(MOCK_TRAINS)
        train = MOCK_TRAINS[train_idx]

        result = {
            "pnr_number": pnr_number,
            "train_number": train["train_number"],
            "train_name": train["train_name"],
            "from_station": train["source"],
            "to_station": train["destination"],
            "journey_date": (datetime.utcnow() + timedelta(days=3)).strftime("%Y-%m-%d"),
            "class_code": "3A",
            "chart_prepared": seed % 2 == 0,
            "passengers": [
                {
                    "name": "PASSENGER 1",
                    "booking_status": "CNF/B1/45",
                    "current_status": "CNF/B1/45",
                    "coach": "B1",
                    "seat": "45",
                }
            ],
        }

        if self.cache:
            await self.cache.set(self.cache.pnr_key(pnr_number), result, ttl=120)

        return result

    async def get_live_status(
        self,
        train_number: str,
        date: Optional[str] = None,
    ) -> Dict[str, Any]:
        if self.cache:
            cache_key = self.cache.train_live_key(train_number, date)
            cached = await self.cache.get(cache_key)
            if cached:
                return cached

        train = next((t for t in MOCK_TRAINS if t["train_number"] == train_number), MOCK_TRAINS[0])

        stations = [
            {
                "station_code": "NDLS",
                "station_name": "New Delhi",
                "scheduled_arrival": None,
                "actual_arrival": None,
                "scheduled_departure": train["departure_time"],
                "actual_departure": train["departure_time"],
                "delay_minutes": 0,
                "platform": "1",
            },
            {
                "station_code": "CNB",
                "station_name": "Kanpur Central",
                "scheduled_arrival": "22:30",
                "actual_arrival": "22:45",
                "scheduled_departure": "22:35",
                "actual_departure": "22:50",
                "delay_minutes": 15,
                "platform": "3",
            },
            {
                "station_code": train["destination"],
                "station_name": next(
                    (s["station_name"] for s in MOCK_STATIONS if s["station_code"] == train["destination"]),
                    train["destination"],
                ),
                "scheduled_arrival": train["arrival_time"],
                "actual_arrival": None,
                "scheduled_departure": None,
                "actual_departure": None,
                "delay_minutes": 15,
                "platform": "5",
            },
        ]

        result = {
            "train_number": train_number,
            "train_name": train["train_name"],
            "current_station": "CNB",
            "last_updated": datetime.utcnow().isoformat(),
            "stations": stations,
        }

        if self.cache:
            await self.cache.set(self.cache.train_live_key(train_number, date), result, ttl=60)

        return result

    async def get_schedule(self, train_number: str) -> Dict[str, Any]:
        if self.cache:
            cache_key = self.cache.train_schedule_key(train_number)
            cached = await self.cache.get(cache_key)
            if cached:
                return cached

        train = next((t for t in MOCK_TRAINS if t["train_number"] == train_number), None)
        if not train:
            raise NotFoundError(f"Train {train_number} not found")

        stops = [
            {
                "station_code": train["source"],
                "station_name": next(
                    (s["station_name"] for s in MOCK_STATIONS if s["station_code"] == train["source"]),
                    train["source"],
                ),
                "arrival_time": None,
                "departure_time": train["departure_time"],
                "day": 1,
                "distance_km": 0,
                "halt_minutes": 0,
            },
            {
                "station_code": "CNB",
                "station_name": "Kanpur Central",
                "arrival_time": "22:30",
                "departure_time": "22:35",
                "day": 1,
                "distance_km": 440,
                "halt_minutes": 5,
            },
            {
                "station_code": train["destination"],
                "station_name": next(
                    (s["station_name"] for s in MOCK_STATIONS if s["station_code"] == train["destination"]),
                    train["destination"],
                ),
                "arrival_time": train["arrival_time"],
                "departure_time": None,
                "day": 2,
                "distance_km": 1384,
                "halt_minutes": 0,
            },
        ]

        result = {
            "train_number": train_number,
            "train_name": train["train_name"],
            "source": train["source"],
            "destination": train["destination"],
            "running_days": "Daily",
            "stops": stops,
        }

        if self.cache:
            await self.cache.set(self.cache.train_schedule_key(train_number), result)

        return result

    async def search_stations(self, query: str) -> List[Dict[str, Any]]:
        if self.cache:
            cache_key = self.cache.station_search_key(query)
            cached = await self.cache.get(cache_key)
            if cached:
                return cached

        query_lower = query.lower()
        db_results = await self.db.execute(
            select(Station).where(
                or_(
                    Station.station_code.ilike(f"%{query}%"),
                    Station.station_name.ilike(f"%{query}%"),
                    Station.city.ilike(f"%{query}%"),
                )
            ).limit(20)
        )
        stations = db_results.scalars().all()

        if stations:
            results = [
                {
                    "id": s.id,
                    "station_code": s.station_code,
                    "station_name": s.station_name,
                    "city": s.city,
                    "state": s.state,
                    "zone": s.zone,
                    "latitude": s.latitude,
                    "longitude": s.longitude,
                }
                for s in stations
            ]
        else:
            results = [
                s for s in MOCK_STATIONS
                if query_lower in s["station_code"].lower()
                or query_lower in s["station_name"].lower()
                or query_lower in s["city"].lower()
            ]

        if self.cache:
            await self.cache.set(self.cache.station_search_key(query), results)

        return results

    async def get_station_by_code(self, station_code: str) -> Station:
        result = await self.db.execute(
            select(Station).where(Station.station_code == station_code.upper())
        )
        station = result.scalar_one_or_none()
        if not station:
            mock = next((s for s in MOCK_STATIONS if s["station_code"] == station_code.upper()), None)
            if not mock:
                raise NotFoundError(f"Station {station_code} not found")
            station = Station(**mock)
        return station

    async def add_favorite_train(
        self,
        user_id: int,
        train_number: str,
        train_name: Optional[str] = None,
        nickname: Optional[str] = None,
    ) -> FavoriteTrain:
        favorite = FavoriteTrain(
            user_id=user_id,
            train_number=train_number,
            train_name=train_name,
            nickname=nickname,
        )
        self.db.add(favorite)
        await self.db.flush()
        return favorite

    async def get_favorite_trains(self, user_id: int) -> List[FavoriteTrain]:
        result = await self.db.execute(
            select(FavoriteTrain).where(FavoriteTrain.user_id == user_id).order_by(FavoriteTrain.created_at.desc())
        )
        return list(result.scalars().all())

    async def remove_favorite_train(self, user_id: int, favorite_id: int) -> None:
        result = await self.db.execute(
            select(FavoriteTrain).where(
                FavoriteTrain.id == favorite_id,
                FavoriteTrain.user_id == user_id,
            )
        )
        favorite = result.scalar_one_or_none()
        if not favorite:
            raise NotFoundError("Favorite train not found")
        await self.db.delete(favorite)

    async def seed_trains_and_stations(self) -> None:
        for station_data in MOCK_STATIONS:
            existing = await self.db.execute(
                select(Station).where(Station.station_code == station_data["station_code"])
            )
            if not existing.scalar_one_or_none():
                self.db.add(Station(**station_data))

        for train_data in MOCK_TRAINS:
            existing = await self.db.execute(
                select(Train).where(Train.train_number == train_data["train_number"])
            )
            if not existing.scalar_one_or_none():
                self.db.add(Train(
                    train_number=train_data["train_number"],
                    train_name=train_data["train_name"],
                    train_type=train_data["train_type"],
                    source_station_code=train_data["source"],
                    destination_station_code=train_data["destination"],
                    departure_time=train_data["departure_time"],
                    arrival_time=train_data["arrival_time"],
                    running_days="Daily",
                ))

        await self.db.flush()
