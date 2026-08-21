"""Hardware controller service — orchestrates validation and serial commands.

Implements the full validation chain:
  device exists → device online → correct mode → e-stop inactive →
  duration valid → not spraying → command not duplicate →
  command not stale → send to ESP32
"""

import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Optional
from threading import RLock

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.database import init_sync_db, sync_engine
from app.models.device import Device
from app.models.spray_event import SprayEvent
from app.services.serial_manager import serial_manager
from app.schemas.common import error_response, success_response
from sqlalchemy.orm import Session, sessionmaker

logger = logging.getLogger(__name__)

# Valid operating modes
VALID_MODES = {"auto", "assisted", "manual"}
EVENT_PENDING = "PENDING"
EVENT_STARTED = "STARTED"
EVENT_COMPLETED = "COMPLETED"
EVENT_STOPPED = "STOPPED"
EVENT_FAILED = "FAILED"

SyncSession = sessionmaker(bind=sync_engine, expire_on_commit=False)


class HardwareController:
    """Orchestrates command validation and ESP32 communication."""

    def __init__(self):
        init_sync_db()
        self._current_mode: str = "manual"
        self._is_spraying: bool = False
        self._is_emergency_stopped: bool = False
        self._last_spray_time: float = 0
        self._state_lock = RLock()
        self._recover_unfinished_events()
        self._load_default_mode()

    def _recover_unfinished_events(self):
        """Do not replay commands left active when the backend stopped."""
        with SyncSession() as session:
            events = session.scalars(
                select(SprayEvent).where(
                    SprayEvent.status.in_([EVENT_PENDING, EVENT_STARTED])
                )
            )
            for event in events:
                event.status = EVENT_FAILED
                event.error_message = "Backend restarted before hardware completion was confirmed"
                event.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
            session.commit()

    def _load_default_mode(self):
        with SyncSession() as session:
            device = session.scalar(select(Device).where(Device.device_uid == "device-001"))
            if device:
                self._current_mode = device.mode

    def _upsert_device(self, session: Session, device_uid: str, status: str = "online") -> Device:
        device = session.scalar(select(Device).where(Device.device_uid == device_uid))
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        if device is None:
            device = Device(device_uid=device_uid, status=status, mode="manual")
            session.add(device)
        device.status = status
        device.last_seen_at = now
        return device

    def _active_event(self, session: Session, device_id: str) -> Optional[SprayEvent]:
        return session.scalar(
            select(SprayEvent)
            .join(Device, SprayEvent.device_id == Device.id)
            .where(
                Device.device_uid == device_id,
                SprayEvent.status.in_([EVENT_PENDING, EVENT_STARTED]),
            )
            .order_by(SprayEvent.id.desc())
        )

    def _fail_active_events(self, session: Session, message: str):
        events = session.scalars(
            select(SprayEvent).where(
                SprayEvent.status.in_([EVENT_PENDING, EVENT_STARTED])
            )
        )
        for event in events:
            event.status = EVENT_FAILED
            event.error_message = message
            event.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)

    def _set_event_status(
        self,
        event_id: int,
        status: str,
        error_message: Optional[str] = None,
    ):
        with SyncSession() as session:
            event = session.get(SprayEvent, event_id)
            if event:
                event.status = status
                event.error_message = error_message
                if status in {EVENT_COMPLETED, EVENT_STOPPED, EVENT_FAILED}:
                    event.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
                session.commit()

    @property
    def current_mode(self) -> str:
        return self._current_mode

    @property
    def is_spraying(self) -> bool:
        return self._is_spraying

    @property
    def is_emergency_stopped(self) -> bool:
        return self._is_emergency_stopped

    def set_mode(self, mode: str, device_id: str = "device-001") -> dict:
        """Set operating mode (auto/assisted/manual)."""
        if mode not in VALID_MODES:
            return error_response("INVALID_MODE", f"Mode must be one of: {', '.join(VALID_MODES)}")

        if self._is_spraying:
            return error_response("DEVICE_BUSY", "Cannot change mode while spraying")

        with SyncSession() as session:
            device = self._upsert_device(session, device_id)
            device.mode = mode
            session.commit()
        self._current_mode = mode
        logger.info(f"Mode set to: {mode}")
        return success_response({"mode": mode})

    def manual_spray(
        self,
        device_id: str,
        duration_ms: int,
        command_id: Optional[str] = None,
    ) -> dict:
        """Execute manual spray with full validation chain (pump-only)."""

        # Generate command ID if not provided
        if not command_id:
            command_id = f"cmd-{uuid.uuid4().hex[:8]}"

        with self._state_lock:
            return self._manual_spray_locked(device_id, duration_ms, command_id)

    def _manual_spray_locked(
        self,
        device_id: str,
        duration_ms: int,
        command_id: str,
    ) -> dict:

        # --- Validation Chain ---

        with SyncSession() as session:
            connected = serial_manager.is_connected
            device = self._upsert_device(
                session,
                device_id,
                status="online" if connected else "offline",
            )
            persisted_mode = device.mode

            # 1. Device online check
            if not connected:
                session.commit()
                return error_response("DEVICE_OFFLINE", "ESP32 is not connected", command_id)

            # 2. Correct operating mode
            if self._current_mode != "manual":
                session.commit()
                return error_response(
                    "WRONG_MODE",
                    f"Manual spray requires MANUAL mode, current: {self._current_mode}",
                    command_id,
                )

            if persisted_mode != self._current_mode:
                self._current_mode = persisted_mode
                if self._current_mode != "manual":
                    session.commit()
                    return error_response(
                        "WRONG_MODE",
                        f"Manual spray requires MANUAL mode, current: {self._current_mode}",
                        command_id,
                    )

            # 3. Emergency stop check
            if self._is_emergency_stopped:
                session.commit()
                return error_response("EMERGENCY_STOP_ACTIVE", "Emergency stop is active", command_id)

            # 4. Duration validation
            if duration_ms < settings.min_pump_duration_ms or duration_ms > settings.max_pump_duration_ms:
                session.commit()
                return error_response(
                    "INVALID_DURATION",
                    f"Duration must be {settings.min_pump_duration_ms}-{settings.max_pump_duration_ms}ms, got {duration_ms}",
                    command_id,
                )

            # 5. Persistent idempotency and active spray checks
            existing = session.scalar(select(SprayEvent).where(SprayEvent.command_id == command_id))
            if existing:
                session.commit()
                return error_response("DUPLICATE_COMMAND", f"Command {command_id} already processed", command_id)

            if self._is_spraying or self._active_event(session, device_id):
                session.commit()
                return error_response("ALREADY_SPRAYING", "A spray operation is already in progress", command_id)

            event = SprayEvent(
                device_id=device.id,
                mode=self._current_mode,
                duration_ms=duration_ms,
                status=EVENT_PENDING,
                command_id=command_id,
            )
            session.add(event)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                return error_response("DUPLICATE_COMMAND", f"Command {command_id} already processed", command_id)
            event_id = event.id

        # --- Send to ESP32 ---
        command = f"SPRAY,{duration_ms}"
        response = serial_manager.send_command(command)

        if response is None:
            with SyncSession() as session:
                device = self._upsert_device(session, device_id, status="error")
                session.commit()
            self._set_event_status(event_id, EVENT_FAILED, "No response from ESP32")
            return error_response("COMMUNICATION_ERROR", "No response from ESP32", command_id)

        if response.startswith("ACK,SPRAY_STARTED"):
            self._set_event_status(event_id, EVENT_STARTED)
            self._is_spraying = True
            self._last_spray_time = time.time()
            return success_response({
                "command_id": command_id,
                "status": "spray_started",
                "duration_ms": duration_ms,
                "esp32_response": response,
            })

        self._set_event_status(event_id, EVENT_FAILED, response)
        if response.startswith("ACK,ERROR"):
            parts = response.split(",")
            error_code = parts[2] if len(parts) > 2 else "UNKNOWN"
            return error_response(
                f"ESP32_{error_code}",
                f"ESP32 rejected command: {response}",
                command_id,
            )

        return error_response("UNEXPECTED_RESPONSE", f"Unexpected ESP32 response: {response}", command_id)

    def stop(self, device_id: str) -> dict:
        """Send stop command to ESP32."""
        if not serial_manager.is_connected:
            return error_response("DEVICE_OFFLINE", "ESP32 is not connected")

        response = serial_manager.send_command("STOP")

        if response and response.startswith("ACK,STOPPED"):
            with SyncSession() as session:
                event = self._active_event(session, device_id)
                if event:
                    event.status = EVENT_STOPPED
                    event.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
                    session.commit()
            self._is_spraying = False
            return success_response({"status": "stopped"})

        if response is None:
            return error_response("COMMUNICATION_ERROR", "No response from ESP32")

        return error_response("UNEXPECTED_RESPONSE", f"Unexpected ESP32 response: {response}")

    def emergency_stop(self) -> dict:
        """Software emergency stop — no confirmation dialog."""
        self._is_emergency_stopped = True
        self._is_spraying = False

        with SyncSession() as session:
            self._fail_active_events(session, "Emergency stop activated before completion")
            session.commit()

        if serial_manager.is_connected:
            serial_manager.send_command("ESTOP")

        return success_response({"status": "emergency_stopped"})

    def reset_emergency_stop(self) -> dict:
        """Reset the emergency stop only after the ESP32 confirms it."""
        if not serial_manager.is_connected:
            return error_response("DEVICE_OFFLINE", "ESP32 is not connected")

        response = serial_manager.send_command("RESET_ESTOP")
        if response is None:
            return error_response("COMMUNICATION_ERROR", "No response from ESP32")

        if response.startswith("ACK,ESTOP_RESET"):
            self._is_emergency_stopped = False
            return success_response({"status": "emergency_stop_reset"})

        if response.startswith("ACK,ERROR,ESTOP_STILL_PRESSED"):
            return error_response("ESTOP_STILL_PRESSED", "Physical emergency stop is still pressed")

        return error_response("UNEXPECTED_RESPONSE", f"Unexpected ESP32 response: {response}")

    def get_status(self, device_id: str) -> dict:
        """Query ESP32 status."""
        if not serial_manager.is_connected:
            with SyncSession() as session:
                device = self._upsert_device(session, device_id, status="offline")
                event = self._active_event(session, device_id)
                if event:
                    event.status = EVENT_FAILED
                    event.error_message = "Communication lost before hardware completion was confirmed"
                    event.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
                session.commit()
            return success_response({
                "device_uid": device_id,
                "status": "offline",
                "mode": self._current_mode,
                "is_spraying": False,
                "is_emergency_stopped": self._is_emergency_stopped,
            })

        response = serial_manager.send_command("STATUS")

        with SyncSession() as session:
            device = self._upsert_device(session, device_id, status="online")
            if self._current_mode == "manual" and device.mode != self._current_mode:
                self._current_mode = device.mode
            session.commit()

        status_data = {
            "device_uid": device_id,
            "status": "online",
            "mode": self._current_mode,
            "is_spraying": self._is_spraying,
            "is_emergency_stopped": self._is_emergency_stopped,
            "firmware_version": None,
            "pump_runtime_ms": None,
        }

        # Parse STATUS response: STATUS,OK,PUMP,OFF,RUNTIME,0,FW,0.2.0
        if response and response.startswith("STATUS,"):
            parts = response.split(",")
            try:
                if "ESTOP" in parts:
                    status_data["is_emergency_stopped"] = True
                    self._is_emergency_stopped = True
                for i, part in enumerate(parts):
                    if part == "PUMP" and i + 1 < len(parts):
                        status_data["is_spraying"] = parts[i + 1] == "ON"
                        self._is_spraying = parts[i + 1] == "ON"
                    elif part == "RUNTIME" and i + 1 < len(parts):
                        status_data["pump_runtime_ms"] = int(parts[i + 1])
                    elif part == "FW" and i + 1 < len(parts):
                        status_data["firmware_version"] = parts[i + 1]
            except (ValueError, IndexError):
                logger.warning(f"Error parsing STATUS response: {response}")

        if response and "PUMP,OFF" in response and "STATUS,ESTOP," not in response:
            with SyncSession() as session:
                event = self._active_event(session, device_id)
                if event:
                    event.status = EVENT_COMPLETED
                    event.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
                    session.commit()
                    self._is_spraying = False
        elif response and "STATUS,ESTOP," in response:
            with SyncSession() as session:
                event = self._active_event(session, device_id)
                if event:
                    event.status = EVENT_FAILED
                    event.error_message = "Emergency stop reported before completion"
                    event.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
                    session.commit()

        return success_response(status_data)

    def get_history(self, device_id: Optional[str] = None, limit: int = 50) -> list[dict]:
        """Return UI-safe persistent spray history."""
        with SyncSession() as session:
            query = (
                select(SprayEvent, Device.device_uid)
                .join(Device, SprayEvent.device_id == Device.id)
                .order_by(SprayEvent.id.desc())
                .limit(limit)
            )
            if device_id:
                query = query.where(Device.device_uid == device_id)

            return [
                {
                    "id": event.id,
                    "device_id": uid,
                    "mode": event.mode,
                    "duration_ms": event.duration_ms,
                    "status": event.status,
                    "command_id": event.command_id,
                    "error_message": event.error_message,
                    "started_at": event.started_at.isoformat() if event.started_at else None,
                    "completed_at": event.completed_at.isoformat() if event.completed_at else None,
                }
                for event, uid in session.execute(query).all()
            ]


# Singleton instance
hardware_controller = HardwareController()
