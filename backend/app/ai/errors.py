"""Errors raised by the local AI subsystem."""


class AIError(Exception):
    """Base class for expected AI subsystem failures."""


class CameraError(AIError):
    """Camera could not be opened or returned a frame."""


class ModelLoadError(AIError):
    """YOLO weights could not be loaded."""


class DetectionError(AIError):
    """Model inference returned an unusable result or failed."""
