import json
from typing import Any, Optional

import redis.asyncio as aioredis

from app.core.config import settings


class RedisCache:
    def __init__(self, redis_client: aioredis.Redis):
        self.redis = redis_client
        self.default_ttl = settings.redis_cache_ttl

    async def get(self, key: str) -> Optional[Any]:
        value = await self.redis.get(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        serialized = json.dumps(value) if not isinstance(value, str) else value
        await self.redis.set(key, serialized, ex=ttl or self.default_ttl)

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)

    async def delete_pattern(self, pattern: str) -> None:
        cursor = 0
        while True:
            cursor, keys = await self.redis.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                await self.redis.delete(*keys)
            if cursor == 0:
                break

    def train_search_key(self, source: str, destination: str, date: Optional[str] = None) -> str:
        date_part = date or "any"
        return f"train:search:{source.upper()}:{destination.upper()}:{date_part}"

    def train_schedule_key(self, train_number: str) -> str:
        return f"train:schedule:{train_number}"

    def train_live_key(self, train_number: str, date: Optional[str] = None) -> str:
        date_part = date or "today"
        return f"train:live:{train_number}:{date_part}"

    def pnr_key(self, pnr_number: str) -> str:
        return f"train:pnr:{pnr_number}"

    def station_search_key(self, query: str) -> str:
        return f"station:search:{query.lower()}"
