"""Pytest configuration and fixtures."""

import os
import pytest
from httpx import AsyncClient, ASGITransport

# Force mock mode for tests
os.environ["ESP32_CONNECTION"] = "mock"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_smartspray.db"

from app.main import app  # noqa: E402
from app.services.hardware_controller import HardwareController  # noqa: E402


@pytest.fixture
def anyio_backend():
    return "asyncio"


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
