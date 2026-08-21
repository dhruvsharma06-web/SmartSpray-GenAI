from typing import Any
from app.ai.detector import Detector
from app.ai.schemas import DetectionResult

class LesionSegmenterAdapter:
    def __init__(self, detector: Detector):
        self.detector = detector

    def segment(self, leaf_crop: Any) -> DetectionResult:
        return self.detector.detect(leaf_crop)
