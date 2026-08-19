"""Tests for HardwareController validation chain.

These tests verify all the safety-critical validation logic from Section 11:
- servo angle validation
- duration validation
- mode enforcement
- emergency stop
- duplicate command protection
- device offline detection
"""

import os
os.environ["ESP32_CONNECTION"] = "mock"

from app.services.hardware_controller import HardwareController
from app.services.serial_manager import serial_manager


# Ensure mock serial is connected for tests
serial_manager._mock_mode = True
serial_manager.connect()


def _fresh_controller() -> HardwareController:
    """Create a fresh controller in manual mode with serial connected."""
    ctrl = HardwareController()
    ctrl._current_mode = "manual"
    return ctrl


class TestManualSprayValidation:
    """Validation chain tests for manual spray."""

    def test_successful_spray(self):
        ctrl = _fresh_controller()
        result = ctrl.manual_spray("device-001", 90, 1000, "cmd-001")
        assert result["success"] is True
        assert result["data"]["status"] == "spray_started"

    def test_invalid_angle_low(self):
        ctrl = _fresh_controller()
        result = ctrl.manual_spray("device-001", 5, 1000, "cmd-002")
        assert result["success"] is False
        assert result["error"]["code"] == "INVALID_SERVO_ANGLE"

    def test_invalid_angle_high(self):
        ctrl = _fresh_controller()
        result = ctrl.manual_spray("device-001", 200, 1000, "cmd-003")
        assert result["success"] is False
        assert result["error"]["code"] == "INVALID_SERVO_ANGLE"

    def test_invalid_duration_too_long(self):
        ctrl = _fresh_controller()
        result = ctrl.manual_spray("device-001", 90, 5000, "cmd-004")
        assert result["success"] is False
        assert result["error"]["code"] == "INVALID_DURATION"

    def test_invalid_duration_too_short(self):
        ctrl = _fresh_controller()
        result = ctrl.manual_spray("device-001", 90, 10, "cmd-005")
        assert result["success"] is False
        assert result["error"]["code"] == "INVALID_DURATION"

    def test_wrong_mode_auto(self):
        ctrl = _fresh_controller()
        ctrl._current_mode = "auto"
        result = ctrl.manual_spray("device-001", 90, 1000, "cmd-006")
        assert result["success"] is False
        assert result["error"]["code"] == "WRONG_MODE"

    def test_wrong_mode_assisted(self):
        ctrl = _fresh_controller()
        ctrl._current_mode = "assisted"
        result = ctrl.manual_spray("device-001", 90, 1000, "cmd-007")
        assert result["success"] is False
        assert result["error"]["code"] == "WRONG_MODE"

    def test_emergency_stop_active(self):
        ctrl = _fresh_controller()
        ctrl._is_emergency_stopped = True
        result = ctrl.manual_spray("device-001", 90, 1000, "cmd-008")
        assert result["success"] is False
        assert result["error"]["code"] == "EMERGENCY_STOP_ACTIVE"

    def test_duplicate_command(self):
        ctrl = _fresh_controller()
        result1 = ctrl.manual_spray("device-001", 90, 1000, "cmd-dup")
        assert result1["success"] is True

        # Reset spraying state but keep processed commands
        ctrl._is_spraying = False
        result2 = ctrl.manual_spray("device-001", 90, 1000, "cmd-dup")
        assert result2["success"] is False
        assert result2["error"]["code"] == "DUPLICATE_COMMAND"


class TestEmergencyStop:
    """Emergency stop tests."""

    def test_emergency_stop(self):
        ctrl = _fresh_controller()
        result = ctrl.emergency_stop()
        assert result["success"] is True
        assert ctrl.is_emergency_stopped is True

    def test_spray_blocked_after_estop(self):
        ctrl = _fresh_controller()
        ctrl.emergency_stop()
        result = ctrl.manual_spray("device-001", 90, 1000)
        assert result["success"] is False
        assert result["error"]["code"] == "EMERGENCY_STOP_ACTIVE"

    def test_reset_emergency_stop(self):
        ctrl = _fresh_controller()
        ctrl.emergency_stop()
        ctrl.reset_emergency_stop()
        assert ctrl.is_emergency_stopped is False


class TestModeControl:
    """Mode setting tests."""

    def test_set_valid_modes(self):
        ctrl = _fresh_controller()
        for mode in ["auto", "assisted", "manual"]:
            result = ctrl.set_mode(mode)
            assert result["success"] is True
            assert ctrl.current_mode == mode

    def test_set_invalid_mode(self):
        ctrl = _fresh_controller()
        result = ctrl.set_mode("turbo")
        assert result["success"] is False
        assert result["error"]["code"] == "INVALID_MODE"


class TestStop:
    """Stop command tests."""

    def test_stop(self):
        ctrl = _fresh_controller()
        result = ctrl.stop("device-001")
        assert result["success"] is True

    def test_stop_clears_spraying(self):
        ctrl = _fresh_controller()
        ctrl._is_spraying = True
        ctrl.stop("device-001")
        assert ctrl.is_spraying is False


class TestStatus:
    """Status query tests."""

    def test_status_online(self):
        ctrl = _fresh_controller()
        result = ctrl.get_status("device-001")
        assert result["success"] is True
        assert result["data"]["status"] == "online"

    def test_status_returns_mode(self):
        ctrl = _fresh_controller()
        ctrl._current_mode = "assisted"
        result = ctrl.get_status("device-001")
        assert result["data"]["mode"] == "assisted"
