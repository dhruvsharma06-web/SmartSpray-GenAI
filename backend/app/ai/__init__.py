"""Local webcam and YOLO inference primitives.

This package returns detections only. It has no hardware or spray-control imports.
"""

from app.ai.detector import Detector
from app.ai.model_loader import ModelLoader
from app.ai.schemas import BoundingBox, Detection, DetectionResult

__all__ = ["BoundingBox", "Detection", "DetectionResult", "Detector", "ModelLoader"]
