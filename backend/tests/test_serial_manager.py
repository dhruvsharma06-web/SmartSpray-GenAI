"""Tests for SerialManager mock mode — pump-only protocol.

Mock protocol must match real ESP32 firmware:
  SPRAY,<duration_ms>  →  ACK,SPRAY_STARTED,<duration_ms>

Malformed command tests verify safe rejection of:
  SPRAY / SPRAY, / SPRAY,abc / SPRAY,-1 / SPRAY,0 / SPRAY,<too large> / SPRAY,1000,EXTRA
"""

import os
os.environ["ESP32_CONNECTION"] = "mock"

from app.services.serial_manager import SerialManager


def _mgr() -> SerialManager:
    mgr = SerialManager()
    mgr._mock_mode = True
    mgr.connect()
    return mgr


def test_mock_mode_detection():
    """SerialManager detects mock mode from config."""
    mgr = _mgr()
    assert mgr.is_mock is True


def test_mock_connect():
    mgr = _mgr()
    assert mgr.is_connected is True


def test_mock_spray_pump_only():
    """Pump-only protocol: SPRAY,<duration_ms>"""
    mgr = _mgr()
    resp = mgr.send_command("SPRAY,1000")
    assert resp is not None
    assert "SPRAY_STARTED" in resp
    assert "1000" in resp


def test_mock_stop_command():
    mgr = _mgr()
    resp = mgr.send_command("STOP")
    assert resp == "ACK,STOPPED"


def test_mock_status_command():
    mgr = _mgr()
    resp = mgr.send_command("STATUS")
    assert resp is not None
    assert resp.startswith("STATUS,")
    # STATUS must NOT contain SERVO
    assert "SERVO" not in resp
    assert "PUMP" in resp


def test_mock_estop_command():
    mgr = _mgr()
    resp = mgr.send_command("ESTOP")
    assert resp == "ACK,ESTOP_ACTIVATED"


def test_mock_invalid_duration():
    mgr = _mgr()
    resp = mgr.send_command("SPRAY,5000")  # 5000ms > max 3000ms
    assert "INVALID_DURATION" in resp


def test_mock_malformed_spray_bare():
    """SPRAY with no comma or argument."""
    mgr = _mgr()
    resp = mgr.send_command("SPRAY")
    assert "UNKNOWN_COMMAND" in resp


def test_mock_malformed_spray_trailing_comma():
    """SPRAY, with nothing after comma."""
    mgr = _mgr()
    resp = mgr.send_command("SPRAY,")
    assert "MALFORMED_COMMAND" in resp


def test_mock_malformed_spray_non_numeric():
    """SPRAY,abc — non-numeric duration."""
    mgr = _mgr()
    resp = mgr.send_command("SPRAY,abc")
    assert "MALFORMED_COMMAND" in resp


def test_mock_malformed_spray_negative():
    """SPRAY,-1 — negative duration."""
    mgr = _mgr()
    resp = mgr.send_command("SPRAY,-1")
    assert "INVALID_DURATION" in resp


def test_mock_malformed_spray_zero():
    """SPRAY,0 — zero duration (below min)."""
    mgr = _mgr()
    resp = mgr.send_command("SPRAY,0")
    assert "INVALID_DURATION" in resp


def test_mock_malformed_spray_too_large():
    """SPRAY,<too large> — exceeds max."""
    mgr = _mgr()
    resp = mgr.send_command("SPRAY,99999")
    assert "INVALID_DURATION" in resp


def test_mock_malformed_spray_extra_field():
    """SPRAY,1000,EXTRA — extra field rejected."""
    mgr = _mgr()
    resp = mgr.send_command("SPRAY,1000,EXTRA")
    assert "MALFORMED_COMMAND" in resp


def test_mock_unknown_command():
    mgr = _mgr()
    resp = mgr.send_command("FOOBAR")
    assert "UNKNOWN_COMMAND" in resp


def test_mock_disconnect():
    mgr = _mgr()
    mgr.disconnect()
    assert mgr.is_connected is False
