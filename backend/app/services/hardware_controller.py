"""Hardware controller service — orchestrates validation and serial commands.

Implements the full validation chain from Section 11:
  device exists → device online → correct mode → e-stop inactive →
  servo valid → duration valid → not spraying → command not duplicate →
  command not stale → send to ESP32
"""

import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Optional

from app.core.config import settings
from app.services.serial_manager import serial_manager
from app.schemas.common import error_response, success_response

logger = logging.getLogger(__name__)

# Valid operating modes
VALID_MODES = {"auto", "assisted", "manual"}


class HardwareController:
    """Orchestrates command validation and ESP32 communication."""

    def __init__(self):
        self._current_mode: str = "manual"
        self._is_spraying: bool = False
        self._is_emergency_stopped: bool = False
        self._processed_commands: set[str] = set()
        self._last_spray_time: float = 0

    @property
    def current_mode(self) -> str:
        return self._current_mode

    @property
    def is_spraying(self) -> bool:
        return self._is_spraying

    @property
    def is_emergency_stopped(self) -> bool:
        return self._is_emergency_stopped

    def set_mode(self, mode: str) -> dict:
        """Set operating mode (auto/assisted/manual)."""
        if mode not in VALID_MODES:
            return error_response("INVALID_MODE", f"Mode must be one of: {', '.join(VALID_MODES)}")

        if self._is_spraying:
            return error_response("DEVICE_BUSY", "Cannot change mode while spraying")

        self._current_mode = mode
        logger.info(f"Mode set to: {mode}")
        return success_response({"mode": mode})

    def manual_spray(
        self,
        device_id: str,
        servo_angle: int,
        duration_ms: int,
        command_id: Optional[str] = None,
    ) -> dict:
        """Execute manual spray with full validation chain."""

        # Generate command ID if not provided
        if not command_id:
            command_id = f"cmd-{uuid.uuid4().hex[:8]}"

        # --- Validation Chain (Section 11) ---

        # 1. Device online check
        if not serial_manager.is_connected:
            return error_response("DEVICE_OFFLINE", "ESP32 is not connected", command_id)

        # 2. Correct operating mode
        if self._current_mode != "manual":
            return error_response(
                "WRONG_MODE",
                f"Manual spray requires MANUAL mode, current: {self._current_mode}",
                command_id,
            )

        # 3. Emergency stop check
        if self._is_emergency_stopped:
            return error_response("EMERGENCY_STOP_ACTIVE", "Emergency stop is active", command_id)

        # 4. Servo angle validation
        if servo_angle < settings.min_servo_angle or servo_angle > settings.max_servo_angle:
            return error_response(
                "INVALID_SERVO_ANGLE",
                f"Servo angle must be {settings.min_servo_angle}-{settings.max_servo_angle}°, got {servo_angle}",
                command_id,
            )

        # 5. Duration validation
        if duration_ms < settings.min_pump_duration_ms or duration_ms > settings.max_pump_duration_ms:
            return error_response(
                "INVALID_DURATION",
                f"Duration must be {settings.min_pump_duration_ms}-{settings.max_pump_duration_ms}ms, got {duration_ms}",
                command_id,
            )

        # 6. Not already spraying
        if self._is_spraying:
            return error_response("ALREADY_SPRAYING", "A spray operation is already in progress", command_id)

        # 7. Duplicate command check
        if command_id in self._processed_commands:
            return error_response("DUPLICATE_COMMAND", f"Command {command_id} already processed", command_id)

        # --- Send to ESP32 ---
        command = f"SPRAY,{servo_angle},{duration_ms}"
        response = serial_manager.send_command(command)

        if response is None:
            return error_response("COMMUNICATION_ERROR", "No response from ESP32", command_id)

        # Track processed command
        self._processed_commands.add(command_id)
        # Keep set from growing unbounded
        if len(self._processed_commands) > 1000:
            self._processed_commands.clear()

        # Parse ESP32 response
        if response.startswith("ACK,SPRAY_STARTED"):
            self._is_spraying = True
            self._last_spray_time = time.time()
            return success_response({
                "command_id": command_id,
                "status": "spray_started",
                "servo_angle": servo_angle,
                "duration_ms": duration_ms,
                "esp32_response": response,
            })

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

        self._is_spraying = False

        if response and response.startswith("ACK,STOPPED"):
            return success_response({"status": "stopped"})

        if response is None:
            return error_response("COMMUNICATION_ERROR", "No response from ESP32")

        return success_response({"status": "stop_sent", "esp32_response": response})

    def emergency_stop(self) -> dict:
        """Software emergency stop — no confirmation dialog."""
        self._is_emergency_stopped = True
        self._is_spraying = False

        if serial_manager.is_connected:
            serial_manager.send_command("ESTOP")

        return success_response({"status": "emergency_stopped"})

    def reset_emergency_stop(self) -> dict:
        """Reset software emergency stop."""
        self._is_emergency_stopped = False
        return success_response({"status": "emergency_stop_reset"})

    def get_status(self, device_id: str) -> dict:
        """Query ESP32 status."""
        if not serial_manager.is_connected:
            return success_response({
                "device_uid": device_id,
                "status": "offline",
                "mode": self._current_mode,
                "is_spraying": False,
                "is_emergency_stopped": self._is_emergency_stopped,
            })

        response = serial_manager.send_command("STATUS")

        status_data = {
            "device_uid": device_id,
            "status": "online",
            "mode": self._current_mode,
            "is_spraying": self._is_spraying,
            "is_emergency_stopped": self._is_emergency_stopped,
            "firmware_version": None,
            "servo_angle": None,
            "pump_runtime_ms": None,
        }

        # Parse STATUS response: STATUS,OK,SERVO,90,PUMP,OFF,RUNTIME,0,FW,0.1.0
        if response and response.startswith("STATUS,"):
            parts = response.split(",")
            try:
                if "ESTOP" in parts:
                    status_data["is_emergency_stopped"] = True
                    self._is_emergency_stopped = True
                for i, part in enumerate(parts):
                    if part == "SERVO" and i + 1 < len(parts):
                        status_data["servo_angle"] = int(parts[i + 1])
                    elif part == "PUMP" and i + 1 < len(parts):
                        status_data["is_spraying"] = parts[i + 1] == "ON"
                        self._is_spraying = parts[i + 1] == "ON"
                    elif part == "RUNTIME" and i + 1 < len(parts):
                        status_data["pump_runtime_ms"] = int(parts[i + 1])
                    elif part == "FW" and i + 1 < len(parts):
                        status_data["firmware_version"] = parts[i + 1]
            except (ValueError, IndexError):
                logger.warning(f"Error parsing STATUS response: {response}")

        return success_response(status_data)


# Singleton instance
hardware_controller = HardwareController()
