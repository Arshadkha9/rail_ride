import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.requests import Request

from app import __version__
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import engine, Base
from app.core.deps import close_redis
from app.core.middleware import ErrorHandlingMiddleware, RequestLoggingMiddleware
from app.websockets.tracking import router as ws_router


logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s v%s", settings.app_name, __version__)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    from app.core.database import AsyncSessionLocal
    from app.services.railway_service import RailwayService
    from app.services.seed_service import seed_admin_user

    async with AsyncSessionLocal() as db:
        try:
            service = RailwayService(db)
            await service.seed_trains_and_stations()
            await seed_admin_user(db)
            await db.commit()
            logger.info("Seeded trains, stations, and admin user")
        except Exception as exc:
            await db.rollback()
            logger.warning("Seed data skipped or failed: %s", exc)

    yield

    await close_redis()
    await engine.dispose()
    logger.info("Shutdown complete")


app = FastAPI(
    title=settings.app_name,
    description="RailRide Super App - Railway booking and ride-hailing platform",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = getattr(request.state, "request_id", None)
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": {"errors": exc.errors()},
            },
            "request_id": request_id,
        },
    )


app.include_router(api_router, prefix=settings.api_v1_prefix)
app.include_router(ws_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": __version__,
        "environment": settings.app_env,
    }


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": f"Welcome to {settings.app_name} API",
        "version": __version__,
        "docs": "/docs",
        "health": "/health",
    }
