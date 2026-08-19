"""YOLO-to-DetectionResult adapter with confidence filtering."""

import logging
from typing import Any

from app.ai.errors import DetectionError
from app.ai.model_loader import ModelLoader
from app.ai.schemas import BoundingBox, Detection, DetectionResult
from app.core.config import settings

logger = logging.getLogger(__name__)


class Detector:
    """Run inference and return data only; this class has no hardware dependency."""

    def __init__(
        self,
        model: Any | None = None,
        model_loader: ModelLoader | None = None,
        confidence_threshold: float | None = None,
    ):
        if model is not None and model_loader is not None:
            raise ValueError("Provide model or model_loader, not both")
        self._model = model
        self._model_loader = model_loader
        self.confidence_threshold = (
            settings.ai_confidence_threshold
            if confidence_threshold is None
            else confidence_threshold
        )

    def detect(self, frame: Any) -> DetectionResult:
        """Infer one frame, retaining raw candidates below the threshold."""
        try:
            model = self._model or (self._model_loader.model if self._model_loader else None)
            if model is None:
                raise DetectionError("Detector has no model")
            if not hasattr(model, "predict"):
                raise DetectionError("Model does not expose predict")

            # Request all model candidates so this adapter can retain raw low confidence.
            kwargs = {"source": frame, "conf": 0.0, "verbose": False}
            if self._model_loader and self._model_loader.resolved_device:
                kwargs["device"] = self._model_loader.resolved_device
            results = model.predict(**kwargs)
            detections = self._parse_results(results)
            return DetectionResult.from_detections(detections, self.confidence_threshold)
        except DetectionError:
            raise
        except Exception as exc:
            logger.error("Inference failed: %s", exc)
            raise DetectionError("Inference failed") from exc

    def _parse_results(self, results: Any) -> list[Detection]:
        if results is None:
            raise DetectionError("Model returned no result")
        if not isinstance(results, (list, tuple)):
            results = [results]

        detections: list[Detection] = []
        for result in results:
            boxes = getattr(result, "boxes", None)
            if boxes is None:
                raise DetectionError("Model result has no boxes")
            xyxy = self._values(getattr(boxes, "xyxy", None), "box coordinates")
            confidences = self._values(getattr(boxes, "conf", None), "confidence")
            classes = self._values(getattr(boxes, "cls", None), "class")
            if not (len(xyxy) == len(confidences) == len(classes)):
                raise DetectionError("Model result arrays have mismatched lengths")

            names = getattr(result, "names", None)
            if names is None and self._model_loader:
                names = self._model_loader.class_names
            for coordinates, confidence, class_id in zip(xyxy, confidences, classes):
                if len(coordinates) != 4:
                    raise DetectionError("Model returned an invalid bounding box")
                x1, y1, x2, y2 = (float(value) for value in coordinates)
                if x2 < x1 or y2 < y1:
                    raise DetectionError("Model returned an invalid bounding box")
                confidence_value = float(confidence)
                if confidence_value < 0 or confidence_value > 1:
                    raise DetectionError("Model returned an invalid confidence")
                class_index = int(class_id)
                detections.append(
                    Detection(
                        class_name=self._class_name(names, class_index),
                        confidence=confidence_value,
                        bounding_box=BoundingBox(
                            x=x1,
                            y=y1,
                            width=x2 - x1,
                            height=y2 - y1,
                        ),
                    )
                )
        return detections

    @staticmethod
    def _values(value: Any, label: str) -> list[Any]:
        if value is None:
            raise DetectionError(f"Model result has no {label}")
        if hasattr(value, "tolist"):
            value = value.tolist()
        if not isinstance(value, list):
            raise DetectionError(f"Model returned invalid {label}")
        return value

    @staticmethod
    def _class_name(names: Any, class_index: int) -> str:
        if isinstance(names, dict):
            return str(names.get(class_index, f"class_{class_index}"))
        if isinstance(names, (list, tuple)) and 0 <= class_index < len(names):
            return str(names[class_index])
        return f"class_{class_index}"
