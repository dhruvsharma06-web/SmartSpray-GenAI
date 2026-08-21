import logging
from typing import Any, Dict
import numpy as np
from app.ai.schemas import DetectionPipelineResult, ComponentResult, SeverityResult
from app.ai.adapters.leaf_detector import LeafDetectorAdapter
from app.ai.adapters.lesion_segmenter import LesionSegmenterAdapter
import cv2

logger = logging.getLogger(__name__)

def extract_leaf_mask_hsv(crop: np.ndarray) -> np.ndarray:
    """Extract leaf foreground mask using HSV filtering (Assumes controlled dark/blue background)."""
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)

    # Tuned for green leaves
    lower_green = np.array([25, 40, 40])
    upper_green = np.array([95, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    if num_labels <= 1:
        return np.zeros_like(mask)

    largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
    final_mask = (labels == largest_label).astype(np.uint8) * 255
    return final_mask

class AIPipeline:
    def __init__(self, leaf_detector: LeafDetectorAdapter, lesion_segmenter: LesionSegmenterAdapter):
        self.leaf_detector = leaf_detector
        self.lesion_segmenter = lesion_segmenter

    def process_frame(self, frame: Any) -> DetectionPipelineResult:
        result = DetectionPipelineResult()

        try:
            leaf_res = self.leaf_detector.detect(frame)
            if leaf_res.detected and leaf_res.bounding_box:
                result.leaf = ComponentResult(
                    detected=True,
                    class_name=leaf_res.class_name or "leaf",
                    confidence=leaf_res.confidence,
                    bbox=leaf_res.bounding_box
                )

                # Crop
                x, y = int(leaf_res.bounding_box.x), int(leaf_res.bounding_box.y)
                w, h = int(leaf_res.bounding_box.width), int(leaf_res.bounding_box.height)
                fh, fw = frame.shape[:2]
                x = max(0, min(x, fw - 1))
                y = max(0, min(y, fh - 1))
                w = max(1, min(w, fw - x))
                h = max(1, min(h, fh - y))

                if w < 10 or h < 10:
                    result.uncertain = True
                    return result

                leaf_crop = frame[y:y+h, x:x+w]

                # Foreground extraction
                leaf_mask = extract_leaf_mask_hsv(leaf_crop)
                leaf_pixels = cv2.countNonZero(leaf_mask)

                # Seg
                lesion_res = self.lesion_segmenter.segment(leaf_crop)

                valid_severity = False
                severity_percentage = None
                reason = "NO_VALID_LESION_OVERLAP"

                if lesion_res.detected:
                    result.lesion = ComponentResult(
                        detected=True,
                        class_name=lesion_res.class_name, # Usually "early_blight_lesion"
                        confidence=lesion_res.confidence,
                        bbox=lesion_res.bounding_box,
                        mask_area_pixels=0 # will recompute
                    )

                    if "early_blight_lesion" in str(lesion_res.class_name):
                        result.disease = "early_blight"

                    # Calculate valid lesion mask
                    lesion_mask = np.zeros_like(leaf_mask)
                    for d in lesion_res.detections:
                        if d.mask_polygons:
                            pts = []
                            for p in d.mask_polygons:
                                px, py = int(p[0] * w), int(p[1] * h)
                                pts.append([px, py])
                            if pts:
                                pts = np.array([pts], dtype=np.int32)
                                cv2.fillPoly(lesion_mask, pts, 255)

                    valid_lesion_mask = cv2.bitwise_and(lesion_mask, leaf_mask)
                    lesion_pixels = cv2.countNonZero(valid_lesion_mask)
                    result.lesion.mask_area_pixels = lesion_pixels

                    # MASK QUALITY CHECK
                    if leaf_pixels < 1000:
                        reason = "INSUFFICIENT_LEAF_AREA"
                    elif lesion_pixels < 0 or lesion_pixels > leaf_pixels:
                        reason = "INVALID_LESION_BOUNDS"
                    else:
                        valid_severity = True
                        severity_percentage = (lesion_pixels / leaf_pixels) * 100.0
                        severity_percentage = max(0.0, min(100.0, severity_percentage))

                else:
                    result.disease = "healthy"
                    valid_severity = True
                    severity_percentage = 0.0

                if valid_severity:
                    level = "NO_SPRAY"
                    if severity_percentage > 60:
                        level = "HIGH"
                    elif severity_percentage >= 26:
                        level = "MEDIUM"
                    elif severity_percentage > 0:
                        level = "LOW"
                    result.severity = SeverityResult(percentage=severity_percentage, level=level)
                else:
                    result.severity = None
                    result.uncertain = True
                    logger.warning(f"Severity invalid: {reason}")
            else:
                result.uncertain = True

        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            result.uncertain = True

        return result

def determine_spray_action(result: DetectionPipelineResult, mode: str = "AUTO") -> Dict[str, Any]:
    if result.uncertain:
        return {"recommendation": "NO_SPRAY", "reason": "UNCERTAIN", "auto_permitted": False}

    if not result.disease or result.disease == "healthy":
        return {"recommendation": "NO_SPRAY", "reason": "NO_DISEASE", "auto_permitted": False}

    if not result.severity:
        return {"recommendation": "NO_SPRAY", "reason": "NO_VALID_SEVERITY", "auto_permitted": False}

    s_level = result.severity.level
    auto = False

    if mode == "AUTO" and s_level in ["LOW", "MEDIUM", "HIGH"]:
        auto = True
    elif mode == "MANUAL":
        auto = False

    return {"recommendation": s_level, "reason": "SEVERITY_BASED", "auto_permitted": auto}
