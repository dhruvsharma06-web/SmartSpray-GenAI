"""Thread-safe OpenCV webcam abstraction."""

import logging
from threading import RLock
from typing import Any, Callable

from app.ai.errors import CameraError
from app.ai.schemas import Frame
from app.core.config import settings

logger = logging.getLogger(__name__)


class CameraReadResult:
    """Explicit result for a frame read attempt."""

    def __init__(self, ok: bool, frame: Frame = None, error: str | None = None):
        self.ok = ok
        self.frame = frame
        self.error = error


class Camera:
    """Owns one OpenCV capture handle and never exposes that handle."""

    def __init__(
        self,
        index: int | None = None,
        capture_factory: Callable[[int], Any] | None = None,
    ):
        self.index = settings.ai_camera_index if index is None else index
        self._capture_factory = capture_factory
        self._capture: Any | None = None
        self._lock = RLock()
        self._last_error: str | None = None

    @property
    def last_error(self) -> str | None:
        return self._last_error

    def open(self) -> bool:
        """Open the configured camera; return False for unavailable hardware."""
        if not isinstance(self.index, int) or self.index < 0:
            self._last_error = "Camera index must be a non-negative integer"
            logger.error("Camera initialization failed: invalid index")
            return False

        with self._lock:
            if self.is_open():
                return True
            try:
                factory = self._capture_factory or self._default_factory()
                capture = factory(self.index)
                if capture is None or not capture.isOpened():
                    if capture is not None:
                        capture.release()
                    self._last_error = "Camera is unavailable"
                    logger.error("Camera initialization failed: unavailable camera")
                    return False
                self._capture = capture
                self._last_error = None
                logger.info("Camera initialized")
                return True
            except CameraError as exc:
                self._capture = None
                self._last_error = str(exc)
                logger.error("Camera initialization failed: %s", exc)
                return False
            except Exception as exc:
                self._capture = None
                self._last_error = "Camera initialization failed"
                logger.error("Camera initialization failed: %s", exc)
                return False

    def is_open(self) -> bool:
        with self._lock:
            return self._capture is not None and bool(self._capture.isOpened())

    def read(self) -> CameraReadResult:
        """Read one frame without exposing OpenCV failure exceptions."""
        with self._lock:
            if not self.is_open():
                return CameraReadResult(False, error="CAMERA_NOT_OPEN")
            try:
                ok, frame = self._capture.read()
                if not ok or frame is None:
                    self._last_error = "Frame capture failed"
                    return CameraReadResult(False, error="FRAME_CAPTURE_FAILED")
                return CameraReadResult(True, frame=frame)
            except Exception as exc:
                self._last_error = "Frame capture failed"
                logger.error("Frame capture failed: %s", exc)
                return CameraReadResult(False, error="FRAME_CAPTURE_FAILED")

    def release(self) -> None:
        with self._lock:
            if self._capture is not None:
                try:
                    self._capture.release()
                finally:
                    self._capture = None
            logger.info("Camera released")

    @staticmethod
    def _default_factory() -> Callable[[int], Any]:
        try:
            import cv2
        except ImportError as exc:
            raise CameraError("OpenCV is not installed") from exc
        return cv2.VideoCapture
