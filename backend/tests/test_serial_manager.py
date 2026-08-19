"""Tests for SerialManager in mock mode."""

import os
os.environ["ESP32_CONNECTION"] = "mock"

from app.services.serial_manager import SerialManager


def test_mock_mode_detection():
    """SerialManager detects mock mode from config."""
    mgr = SerialManager()
    mgr._mock_mode = True  # Force mock
    assert mgr.is_mock is True


def test_mock_connect():
    mgr = SerialManager()
    mgr._mock_mode = True
    assert mgr.connect() is True
    assert mgr.is_connected is True


def test_mock_spray_command():
    mgr = SerialManager()
    mgr._mock_mode = True
    mgr.connect()
    resp = mgr.send_command("SPRAY,90,1000")
    assert resp is not None
    assert "SPRAY_STARTED" in resp
    assert "90" in resp
    assert "1000" in resp


def test_mock_stop_command():
    mgr = SerialManager()
    mgr._mock_mode = True
    mgr.connect()
    resp = mgr.send_command("STOP")
    assert resp == "ACK,STOPPED"


def test_mock_status_command():
    mgr = SerialManager()
    mgr._mock_mode = True
    mgr.connect()
    resp = mgr.send_command("STATUS")
    assert resp is not None
    assert resp.startswith("STATUS,")


def test_mock_estop_command():
    mgr = SerialManager()
    mgr._mock_mode = True
    mgr.connect()
    resp = mgr.send_command("ESTOP")
    assert resp == "ACK,ESTOP_ACTIVATED"


def test_mock_invalid_angle():
    mgr = SerialManager()
    mgr._mock_mode = True
    mgr.connect()
    resp = mgr.send_command("SPRAY,5,1000")  # Angle 5 is below min
    assert "INVALID_ANGLE" in resp


def test_mock_invalid_duration():
    mgr = SerialManager()
    mgr._mock_mode = True
    mgr.connect()
    resp = mgr.send_command("SPRAY,90,5000")  # 5000ms > max 3000ms
    assert "INVALID_DURATION" in resp


def test_mock_malformed_command():
    mgr = SerialManager()
    mgr._mock_mode = True
    mgr.connect()
    resp = mgr.send_command("SPRAY,baddata")
    assert "MALFORMED_COMMAND" in resp


def test_mock_unknown_command():
    mgr = SerialManager()
    mgr._mock_mode = True
    mgr.connect()
    resp = mgr.send_command("FOOBAR")
    assert "UNKNOWN_COMMAND" in resp


def test_mock_disconnect():
    mgr = SerialManager()
    mgr._mock_mode = True
    mgr.connect()
    mgr.disconnect()
    assert mgr.is_connected is False
