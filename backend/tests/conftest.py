"""Pytest configuration and fixtures."""

import os
from pathlib import Path
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import delete

# Force mock mode for tests
os.environ["ESP32_CONNECTION"] = "mock"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_smartspray.db"

test_database = Path(__file__).resolve().parents[1] / "test_smartspray.db"
if test_database.exists():
    test_database.unlink()

from app.main import app  # noqa: E402
from app.core.database import sync_engine  # noqa: E402
from app.models.device import Device  # noqa: E402
from app.models.spray_event import SprayEvent  # noqa: E402
from app.services.hardware_controller import HardwareController  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
def reset_persistent_state():
    """Keep tests isolated while preserving persistence within each test."""
    with Session(sync_engine) as session:
        session.execute(delete(SprayEvent))
        session.execute(delete(Device))
        session.commit()


@pytest.fixture
async def client():
    """Async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def controller():
    """Fresh hardware controller for each test."""
    return HardwareController()
