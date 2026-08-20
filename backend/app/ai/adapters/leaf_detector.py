from typing import Any
from app.ai.detector import Detector
from app.ai.schemas import DetectionResult

class LeafDetectorAdapter:
    def __init__(self, detector: Detector):
        self.detector = detector

    def detect(self, frame: Any) -> DetectionResult:
        return self.detector.detect(frame)
