from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router
from app.config import settings
from app.database import Base, engine
from app.services.seed import ensure_demo_account


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Pharmaceutical Distribution SaaS",
    version="0.1.0",
)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routes
app.include_router(
    router,
    prefix="/api/v1",
)


@app.on_event("startup")
async def startup_event() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    await ensure_demo_account()


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to PharmaDistrib API",
        "version": "0.1.0",
        "status": "running",
    }