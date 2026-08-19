"""Persistence and lifecycle tests for the hardware application state."""

from concurrent.futures import ThreadPoolExecutor

import pytest

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import sync_engine
from app.models.device import Device
from app.models.spray_event import SprayEvent
from app.services.hardware_controller import (
    EVENT_COMPLETED,
    EVENT_FAILED,
    EVENT_STARTED,
    EVENT_STOPPED,
    HardwareController,
)
from app.services.serial_manager import serial_manager


serial_manager._mock_mode = True
serial_manager.connect()


def _event(command_id: str) -> SprayEvent:
    with Session(sync_engine) as session:
        return session.scalar(select(SprayEvent).where(SprayEvent.command_id == command_id))


def test_device_upsert_and_mode_survive_controller_restart():
    first = HardwareController()
    assert first.set_mode("assisted", device_id="device-persist")['success'] is True

    second = HardwareController()

    with Session(sync_engine) as session:
        devices = session.scalars(select(Device).where(Device.device_uid == "device-persist")).all()
        assert len(devices) == 1
        assert devices[0].mode == "assisted"
        assert devices[0].last_seen_at is not None


def test_started_and_completed_lifecycle_is_persisted():
    controller = HardwareController()
    result = controller.manual_spray("device-lifecycle", 90, 1000, "lifecycle-start")
    assert result["success"] is True
    assert _event("lifecycle-start").status == EVENT_STARTED

    controller.get_status("device-lifecycle")
    event = _event("lifecycle-start")
    assert event.status == EVENT_COMPLETED
    assert event.completed_at is not None


def test_pending_event_is_committed_before_serial_send(monkeypatch):
    controller = HardwareController()
    observed = {}

    def inspect_before_ack(command):
        observed["status"] = _event("pending-command").status
        return "ACK,SPRAY_STARTED,90,1000"

    monkeypatch.setattr(serial_manager, "send_command", inspect_before_ack)

    result = controller.manual_spray("device-pending", 90, 1000, "pending-command")

    assert result["success"] is True
    assert observed["status"] == "PENDING"


def test_stop_marks_started_event_stopped():
    controller = HardwareController()
    controller.manual_spray("device-stop", 90, 1000, "lifecycle-stop")

    result = controller.stop("device-stop")

    assert result["success"] is True
    assert _event("lifecycle-stop").status == EVENT_STOPPED


def test_failed_esp32_response_is_persisted(monkeypatch):
    controller = HardwareController()
    monkeypatch.setattr(serial_manager, "send_command", lambda command: "ACK,ERROR,INVALID_ANGLE,5")

    result = controller.manual_spray("device-failed", 90, 1000, "lifecycle-failed")

    assert result["success"] is False
    assert _event("lifecycle-failed").status == EVENT_FAILED


def test_communication_failure_is_persisted(monkeypatch):
    controller = HardwareController()
    monkeypatch.setattr(serial_manager, "send_command", lambda command: None)

    result = controller.manual_spray("device-comm-failed", 90, 1000, "lifecycle-comm-failed")

    assert result["success"] is False
    assert _event("lifecycle-comm-failed").status == EVENT_FAILED


def test_duplicate_command_survives_controller_restart():
    first = HardwareController()
    assert first.manual_spray("device-restart", 90, 1000, "restart-command")["success"] is True

    second = HardwareController()
    result = second.manual_spray("device-restart", 90, 1000, "restart-command")

    assert result["success"] is False
    assert result["error"]["code"] == "DUPLICATE_COMMAND"


def test_restart_marks_unfinished_event_failed_without_replay(monkeypatch):
    first = HardwareController()
    first.manual_spray("device-interrupted", 90, 1000, "interrupted-command")

    sent = []
    monkeypatch.setattr(
        serial_manager,
        "send_command",
        lambda command: sent.append(command) or "ACK,SPRAY_STARTED,90,1000",
    )
    second = HardwareController()
    result = second.manual_spray("device-interrupted", 90, 1000, "interrupted-command")

    event = _event("interrupted-command")
    assert result["error"]["code"] == "DUPLICATE_COMMAND"
    assert event.status == EVENT_FAILED
    assert sent == []


def test_disconnect_marks_active_event_failed_without_completion():
    controller = HardwareController()
    controller.manual_spray("device-disconnect", 90, 1000, "disconnect-command")
    serial_manager.disconnect()

    status = controller.get_status("device-disconnect")
    event = _event("disconnect-command")

    assert status["data"]["status"] == "offline"
    assert event.status == EVENT_FAILED
    assert event.error_message is not None
    assert event.completed_at is not None
    serial_manager.connect()


def test_physical_estop_status_cannot_complete_event(monkeypatch):
    controller = HardwareController()
    controller.manual_spray("device-estop", 90, 1000, "estop-command")
    monkeypatch.setattr(
        serial_manager,
        "send_command",
        lambda command: "STATUS,ESTOP,SERVO,90,PUMP,OFF,RUNTIME,0,FW,0.1.0",
    )

    status = controller.get_status("device-estop")
    event = _event("estop-command")

    assert status["data"]["is_emergency_stopped"] is True
    assert event.status == EVENT_FAILED
    assert event.completed_at is not None


def test_concurrent_duplicate_command_does_not_send_twice():
    controller = HardwareController()

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(
            lambda _: controller.manual_spray("device-concurrent", 90, 1000, "concurrent-command"),
            range(2),
        ))

    assert sum(result["success"] for result in results) == 1
    assert sum(result.get("error", {}).get("code") == "DUPLICATE_COMMAND" for result in results) == 1


def test_different_command_is_rejected_while_spray_active():
    controller = HardwareController()
    controller.manual_spray("device-busy", 90, 1000, "busy-first")

    result = controller.manual_spray("device-busy", 90, 1000, "busy-second")

    assert result["success"] is False
    assert result["error"]["code"] == "ALREADY_SPRAYING"


def test_history_returns_ui_safe_persistent_fields():
    controller = HardwareController()
    controller.manual_spray("device-history", 90, 1000, "history-command")

    history = controller.get_history(device_id="device-history")

    assert len(history) == 1
    assert history[0]["command_id"] == "history-command"
    assert history[0]["status"] == EVENT_STARTED
    assert "esp32_response" not in history[0]


@pytest.mark.anyio
async def test_history_api_returns_persisted_events(client):
    response = await client.post(
        "/api/v1/spray/manual",
        json={
            "device_id": "device-history-api",
            "servo_angle": 90,
            "duration_ms": 1000,
            "command_id": "history-api-command",
        },
    )
    assert response.status_code == 200

    response = await client.get("/api/v1/spray/history?device_id=device-history-api")

    assert response.status_code == 200
    assert response.json()["data"][0]["command_id"] == "history-api-command"
