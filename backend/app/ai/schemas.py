"""Structured contracts returned by the AI subsystem."""

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    """Pixel-space bounding box with a top-left origin."""

    x: float = Field(ge=0)
    y: float = Field(ge=0)
    width: float = Field(ge=0)
    height: float = Field(ge=0)


class Detection(BaseModel):
    """One raw model detection, including candidates below the threshold."""

    class_name: str
    confidence: float = Field(ge=0, le=1)
    bounding_box: BoundingBox
    mask_polygons: list[list[float]] | None = None
    mask_area_pixels: float | None = Field(default=None, ge=0)


class DetectionResult(BaseModel):
    """A model result with explicit confidence and uncertainty semantics."""

    detected: bool
    class_name: str | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    bounding_box: BoundingBox | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    uncertainty: bool = False
    detections: list[Detection] = Field(default_factory=list)
    error: str | None = None

    @classmethod
    def no_detection(cls) -> "DetectionResult":
        return cls(detected=False)

    @classmethod
    def uncertain(cls, detections: list[Detection], error: str | None = None) -> "DetectionResult":
        best = max(detections, key=lambda item: item.confidence, default=None)
        return cls(
            detected=False,
            class_name=best.class_name if best else None,
            confidence=best.confidence if best else None,
            bounding_box=best.bounding_box if best else None,
            uncertainty=True,
            detections=detections,
            error=error,
        )

    @classmethod
    def from_detections(cls, detections: list[Detection], threshold: float) -> "DetectionResult":
        if not detections:
            return cls.no_detection()
        best = max(detections, key=lambda item: item.confidence)
        valid = [item for item in detections if item.confidence >= threshold]
        return cls(
            detected=bool(valid),
            class_name=best.class_name,
            confidence=best.confidence,
            bounding_box=best.bounding_box,
            uncertainty=not bool(valid),
            detections=detections,
        )


# Kept as a narrow alias for callers that annotate arbitrary frame types.
Frame = Any

class ComponentResult(BaseModel):
    detected: bool = False
    class_name: str | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    bbox: BoundingBox | None = None
    mask_area_pixels: float | None = None

class SeverityResult(BaseModel):
    percentage: float | None = None
    level: str | None = None

class DetectionPipelineResult(BaseModel):
    leaf: ComponentResult | None = None
    lesion: ComponentResult | None = None
    disease: str | None = None
    severity: SeverityResult | None = None
    uncertain: bool = False
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
