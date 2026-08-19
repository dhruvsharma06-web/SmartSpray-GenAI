"""Tests for API endpoints.

Verifies the API contract from Section 12:
- Success responses: {"success": true, "data": {}}
- Error responses: {"success": false, "error": {"code": "...", "message": "..."}}
"""

import os
os.environ["ESP32_CONNECTION"] = "mock"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_smartspray.db"

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.anyio
async def test_root(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "SmartSpray API"


@pytest.mark.anyio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"


@pytest.mark.anyio
async def test_manual_spray_success(client):
    resp = await client.post("/api/v1/spray/manual", json={
        "device_id": "device-001",
        "servo_angle": 90,
        "duration_ms": 1000,
        "command_id": "test-cmd-api-1",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert data["data"]["status"] == "spray_started"


@pytest.mark.anyio
async def test_manual_spray_invalid_angle(client):
    resp = await client.post("/api/v1/spray/manual", json={
        "device_id": "device-001",
        "servo_angle": 5,
        "duration_ms": 1000,
        "command_id": "test-cmd-api-2",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is False
    assert data["error"]["code"] == "INVALID_SERVO_ANGLE"


@pytest.mark.anyio
async def test_stop(client):
    resp = await client.post("/api/v1/spray/stop", json={
        "device_id": "device-001",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True


@pytest.mark.anyio
async def test_emergency_stop(client):
    resp = await client.post("/api/v1/spray/emergency-stop")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True


@pytest.mark.anyio
async def test_device_status(client):
    # Reset emergency stop first
    await client.post("/api/v1/spray/reset-emergency-stop")

    resp = await client.get("/api/v1/devices/device-001/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "device_uid" in data["data"]


@pytest.mark.anyio
async def test_set_mode(client):
    resp = await client.post("/api/v1/devices/device-001/mode", json={
        "mode": "assisted",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True

    # Reset to manual for other tests
    await client.post("/api/v1/devices/device-001/mode", json={"mode": "manual"})


@pytest.mark.anyio
async def test_set_invalid_mode(client):
    resp = await client.post("/api/v1/devices/device-001/mode", json={
        "mode": "turbo",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is False
    assert data["error"]["code"] == "INVALID_MODE"


@pytest.mark.anyio
async def test_error_response_format(client):
    """Verify error responses match Section 12 format."""
    resp = await client.post("/api/v1/spray/manual", json={
        "device_id": "device-001",
        "servo_angle": 5,
        "duration_ms": 1000,
        "command_id": "test-cmd-format",
    })
    data = resp.json()

    assert "success" in data
    assert data["success"] is False
    assert "error" in data
    assert "code" in data["error"]
    assert "message" in data["error"]
