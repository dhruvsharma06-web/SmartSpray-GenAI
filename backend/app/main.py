"""SmartSpray FastAPI Application."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.services.serial_manager import serial_manager
from app.api.v1 import ai, spray, devices

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.app_env == "development" else logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup
    logger.info(f"SmartSpray Backend starting (env={settings.app_env})")
    await init_db()
    logger.info("Database initialized")

    connected = serial_manager.connect()
    if connected:
        logger.info(
            f"ESP32 connected ({'MOCK' if serial_manager.is_mock else settings.esp32_serial_port})"
        )
    else:
        logger.warning("ESP32 not connected — hardware commands will fail")

    yield

    # Shutdown
    serial_manager.disconnect()
    logger.info("SmartSpray Backend stopped")


app = FastAPI(
    title="SmartSpray API",
    version="0.1.0",
    description="AI + IoT Precision Spraying System",
    lifespan=lifespan,
)

# CORS for Flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 routers
app.include_router(spray.router, prefix="/api/v1")
app.include_router(devices.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "name": "SmartSpray API",
        "version": "0.1.0",
        "status": "running",
        "env": settings.app_env,
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "esp32_connected": serial_manager.is_connected,
        "esp32_mock": serial_manager.is_mock,
    }
