"""Serial communication manager for ESP32.

Supports two modes:
  - "serial": Real USB serial connection via pyserial
  - "mock":   Simulated responses for testing (clearly labeled per Rule 6)
"""

import logging
import threading
import time
from typing import Optional

import serial

from app.core.config import settings

logger = logging.getLogger(__name__)


class SerialManager:
    """Thread-safe serial communication with ESP32."""

    def __init__(self):
        self._connection: Optional[serial.Serial] = None
        self._lock = threading.Lock()
        self._mock_mode = settings.esp32_connection == "mock"
        self._connected = False

    @property
    def is_mock(self) -> bool:
        return self._mock_mode

    @property
    def is_connected(self) -> bool:
        if self._mock_mode:
            return self._connected
        return self._connected and self._connection is not None and self._connection.is_open

    def connect(self) -> bool:
        """Open serial connection to ESP32."""
        if self._mock_mode:
            logger.info("[MOCK MODE] Serial manager initialized in mock mode")
            self._connected = True
            return True

        try:
            with self._lock:
                self._connection = serial.Serial(
                    port=settings.esp32_serial_port,
                    baudrate=settings.esp32_baud_rate,
                    timeout=2.0,
                    write_timeout=2.0,
                )
                time.sleep(2)  # Wait for ESP32 reset after serial connect
                # Flush any boot messages
                self._connection.reset_input_buffer()
                self._connected = True
                logger.info(f"Connected to ESP32 on {settings.esp32_serial_port}")
                return True
        except serial.SerialException as e:
            logger.error(f"Failed to connect to ESP32: {e}")
            self._connected = False
            return False

    def disconnect(self):
        """Close serial connection."""
        if self._mock_mode:
            self._connected = False
            return

        with self._lock:
            if self._connection and self._connection.is_open:
                self._connection.close()
            self._connected = False
            logger.info("Disconnected from ESP32")

    def send_command(self, command: str, timeout: float = 3.0) -> Optional[str]:
        """Send a command and wait for ACK response.

        Returns the response string or None on timeout/error.
        """
        if self._mock_mode:
            return self._mock_response(command)

        if not self.is_connected:
            logger.error("Cannot send command: not connected")
            return None

        try:
            with self._lock:
                # Send command with newline terminator
                self._connection.write(f"{command}\n".encode("utf-8"))
                self._connection.flush()
                logger.debug(f"Sent: {command}")

                # Read response with timeout
                start = time.time()
                while time.time() - start < timeout:
                    if self._connection.in_waiting > 0:
                        line = self._connection.readline().decode("utf-8").strip()
                        if line.startswith("ACK,") or line.startswith("STATUS,"):
                            logger.debug(f"Received: {line}")
                            return line
                        # Skip INFO lines (boot messages, etc.)
                        elif line.startswith("INFO,"):
                            logger.debug(f"Info: {line}")
                            continue
                    time.sleep(0.01)

                logger.warning(f"Timeout waiting for response to: {command}")
                return None

        except serial.SerialException as e:
            logger.error(f"Serial error: {e}")
            self._connected = False
            return None

    def _mock_response(self, command: str) -> str:
        """Generate mock responses matching the real ESP32 protocol. [MOCK MODE]

        Protocol: SPRAY,<duration_ms>
        No servo participation — pump-only architecture.
        """
        logger.info(f"[MOCK MODE] Command: {command}")

        if command == "STOP":
            return "ACK,STOPPED"

        if command == "STATUS":
            return "STATUS,OK,PUMP,OFF,RUNTIME,0,FW,0.2.0"

        if command == "ESTOP":
            return "ACK,ESTOP_ACTIVATED"

        if command == "RESET_ESTOP":
            return "ACK,ESTOP_RESET"

        if command.startswith("SPRAY,"):
            parts = command.split(",")
            if len(parts) == 2:
                try:
                    duration = int(parts[1])

                    if duration < settings.min_pump_duration_ms or duration > settings.max_pump_duration_ms:
                        return f"ACK,ERROR,INVALID_DURATION,{duration}"

                    return f"ACK,SPRAY_STARTED,{duration}"
                except ValueError:
                    return "ACK,ERROR,MALFORMED_COMMAND"

            return "ACK,ERROR,MALFORMED_COMMAND"

        return "ACK,ERROR,UNKNOWN_COMMAND"


# Singleton instance
serial_manager = SerialManager()
