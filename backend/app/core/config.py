from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "RailRide"
    app_env: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    host: str = "0.0.0.0"
    port: int = 8000

    database_url: str = "postgresql+asyncpg://railride:railride_secret@localhost:5432/railride"
    database_url_sync: str = "postgresql://railride:railride_secret@localhost:5432/railride"

    redis_url: str = "redis://localhost:6379/0"
    redis_cache_ttl: int = 300

    secret_key: str = "change-this-to-a-long-random-secret-key-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    otp_expire_minutes: int = 10
    otp_length: int = 6

    railway_api_base_url: str = "https://api.railway.example.com"
    railway_api_key: str = "mock-railway-api-key"

    fare_bike_per_km: float = 8.0
    fare_auto_per_km: float = 12.0
    fare_taxi_per_km: float = 18.0
    base_fare_bike: float = 15.0
    base_fare_auto: float = 25.0
    base_fare_taxi: float = 40.0

    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            import json

            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
