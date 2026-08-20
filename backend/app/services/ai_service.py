import logging
from typing import Any
from app.ai.pipeline import AIPipeline, determine_spray_action
from app.ai.schemas import DetectionPipelineResult
from app.ai.model_loader import ModelLoader
from app.ai.detector import Detector
from app.ai.adapters.leaf_detector import LeafDetectorAdapter
from app.ai.adapters.lesion_segmenter import LesionSegmenterAdapter
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.leaf_loader = ModelLoader(model_path=settings.ai_leaf_model_path)
        self.lesion_loader = ModelLoader(model_path=settings.ai_lesion_model_path)

        self.leaf_detector = Detector(model_loader=self.leaf_loader)
        self.lesion_detector = Detector(model_loader=self.lesion_loader)

        self.pipeline = AIPipeline(
            leaf_detector=LeafDetectorAdapter(self.leaf_detector),
            lesion_segmenter=LesionSegmenterAdapter(self.lesion_detector)
        )

    def load_models(self) -> None:
        self.leaf_loader.load()
        self.lesion_loader.load()

    def is_ready(self) -> bool:
        return self.leaf_loader.ready and self.lesion_loader.ready

    def get_status(self) -> dict:
        return {
            "ready": self.is_ready(),
            "leaf_model": self.leaf_loader.ready,
            "lesion_model": self.lesion_loader.ready,
            "error": self.leaf_loader.load_error or self.lesion_loader.load_error
        }

    def process_frame(self, frame: Any) -> dict:
        if not self.is_ready():
            try:
                self.load_models()
            except Exception as e:
                return {"error": f"Failed to load models: {str(e)}"}

        res = self.pipeline.process_frame(frame)
        decision = determine_spray_action(res)

        return {
            "data": res.model_dump(),
            "decision": decision
        }

ai_service = AIService()
