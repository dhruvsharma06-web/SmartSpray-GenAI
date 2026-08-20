import logging
from typing import Any, Dict

import cv2
import numpy as np

from app.ai.schemas import (
    ComponentResult,
    DetectionPipelineResult,
    SeverityResult,
)
from app.ai.adapters.leaf_detector import LeafDetectorAdapter
from app.ai.adapters.lesion_segmenter import LesionSegmenterAdapter

logger = logging.getLogger(__name__)


def extract_leaf_mask_hsv(crop: np.ndarray) -> np.ndarray:
    """Extract the largest green foreground region from a leaf crop."""
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)

    lower_green = np.array([25, 40, 40])
    upper_green = np.array([95, 255, 255])

    mask = cv2.inRange(hsv, lower_green, upper_green)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
        mask,
        connectivity=8,
    )

    if num_labels <= 1:
        return np.zeros_like(mask)

    largest_label = 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])
    return (labels == largest_label).astype(np.uint8) * 255


class AIPipeline:
    """
    SmartSpray AI pipeline.

    Model 1:
        leaf_detector.pt -> detects the leaf.

    Model 2:
        disease_detector.pt -> detects:
            Healthy
            Early Blight
            Late Blight
            Septoria

    The disease model is a detection model, not a segmentation model,
    so severity is estimated from the disease bounding-box area relative
    to the detected leaf area.
    """

    def __init__(
        self,
        leaf_detector: LeafDetectorAdapter,
        lesion_segmenter: LesionSegmenterAdapter,
    ):
        self.leaf_detector = leaf_detector
        self.lesion_segmenter = lesion_segmenter

    def process_frame(self, frame: Any) -> DetectionPipelineResult:
        result = DetectionPipelineResult()

        try:
            # ---------------------------------------------------------
            # STEP 1: Detect leaf
            # ---------------------------------------------------------
            leaf_res = self.leaf_detector.detect(frame)

            if not leaf_res.detected or not leaf_res.bounding_box:
                result.uncertain = True
                return result

            result.leaf = ComponentResult(
                detected=True,
                class_name=leaf_res.class_name or "leaf",
                confidence=leaf_res.confidence,
                bbox=leaf_res.bounding_box,
            )

            # ---------------------------------------------------------
            # STEP 2: Crop leaf
            # ---------------------------------------------------------
            x = int(leaf_res.bounding_box.x)
            y = int(leaf_res.bounding_box.y)
            w = int(leaf_res.bounding_box.width)
            h = int(leaf_res.bounding_box.height)

            fh, fw = frame.shape[:2]

            x = max(0, min(x, fw - 1))
            y = max(0, min(y, fh - 1))
            w = max(1, min(w, fw - x))
            h = max(1, min(h, fh - y))

            if w < 10 or h < 10:
                result.uncertain = True
                return result

            leaf_crop = frame[y:y + h, x:x + w]

            # ---------------------------------------------------------
            # STEP 3: Estimate actual green leaf area
            # ---------------------------------------------------------
            leaf_mask = extract_leaf_mask_hsv(leaf_crop)
            leaf_pixels = cv2.countNonZero(leaf_mask)

            # If HSV segmentation fails, fall back to the detected
            # leaf bounding-box area rather than declaring the image
            # automatically healthy.
            if leaf_pixels < 1000:
                leaf_pixels = w * h

                        # ---------------------------------------------------------
            # STEP 4: Run disease detector
            # ---------------------------------------------------------
            disease_res = self.lesion_segmenter.segment(leaf_crop)

            # Safety gate: reject low-confidence disease predictions.
            if (
                disease_res.confidence is not None
                and disease_res.confidence < 0.65
            ):
                result.uncertain = True
                result.severity = None
                logger.warning(
                    "Disease confidence below threshold: %.3f",
                    disease_res.confidence,
                )
                return result

            if not disease_res.detections:
                # No disease candidate at all.
                result.disease = "healthy"
                result.severity = SeverityResult(
                    percentage=0.0,
                    level="NO_SPRAY",
                )
                result.uncertain = False
                return result

            # ---------------------------------------------------------
            # STEP 5: Handle Healthy
            # ---------------------------------------------------------
            if normalized_class == "healthy":
                result.lesion = ComponentResult(
                    detected=True,
                    class_name="Healthy",
                    confidence=best_detection.confidence,
                    bbox=best_detection.bounding_box,
                    mask_area_pixels=None,
                )

                result.disease = "healthy"
                result.severity = SeverityResult(
                    percentage=0.0,
                    level="NO_SPRAY",
                )
                result.uncertain = False

                return result

            # ---------------------------------------------------------
            # STEP 6: Map disease class
            # ---------------------------------------------------------
            disease_map = {
                "early blight": "early_blight",
                "late blight": "late_blight",
                "septoria": "septoria",
            }

            disease_name = disease_map.get(normalized_class)

            if disease_name is None:
                logger.warning(
                    "Unknown disease class returned by model: %s",
                    class_name,
                )
                result.uncertain = True
                return result

            result.disease = disease_name

            result.lesion = ComponentResult(
                detected=True,
                class_name=class_name,
                confidence=best_detection.confidence,
                bbox=best_detection.bounding_box,
                mask_area_pixels=None,
            )

            # ---------------------------------------------------------
            # STEP 7: Estimate disease area
            #
            # Disease model is detection-based, so use the bounding
            # box area rather than segmentation pixels.
            # ---------------------------------------------------------
            disease_box = best_detection.bounding_box

            if disease_box is None:
                result.uncertain = True
                result.severity = None
                return result

            disease_area = (
                max(0.0, disease_box.width)
                * max(0.0, disease_box.height)
            )

            if disease_area <= 0 or leaf_pixels <= 0:
                result.uncertain = True
                result.severity = None
                return result

            # ---------------------------------------------------------
            # STEP 8: Calculate severity percentage
            # ---------------------------------------------------------
            severity_percentage = (
                disease_area / float(leaf_pixels)
            ) * 100.0

            severity_percentage = max(
                0.0,
                min(100.0, severity_percentage),
            )

            # ---------------------------------------------------------
            # STEP 9: Convert percentage to severity level
            # ---------------------------------------------------------
            if severity_percentage > 60:
                severity_level = "HIGH"
            elif severity_percentage >= 26:
                severity_level = "MEDIUM"
            elif severity_percentage > 0:
                severity_level = "LOW"
            else:
                severity_level = "NO_SPRAY"

            result.severity = SeverityResult(
                percentage=severity_percentage,
                level=severity_level,
            )

            result.uncertain = False

        except Exception as exc:
            logger.error("Pipeline error: %s", exc)
            result.uncertain = True

        return result


def determine_spray_action(
    result: DetectionPipelineResult,
    mode: str = "AUTO",
) -> Dict[str, Any]:
    """
    Convert AI result into a safe spraying decision.

    Any uncertain result defaults to NO_SPRAY.
    """

    # Safety-first behavior.
    if result.uncertain:
        return {
            "recommendation": "NO_SPRAY",
            "reason": "UNCERTAIN",
            "auto_permitted": False,
        }

    # Healthy plant requires no spraying.
    if not result.disease or result.disease == "healthy":
        return {
            "recommendation": "NO_SPRAY",
            "reason": "NO_DISEASE",
            "auto_permitted": False,
        }

    # Disease exists but severity calculation failed.
    if not result.severity:
        return {
            "recommendation": "NO_SPRAY",
            "reason": "NO_VALID_SEVERITY",
            "auto_permitted": False,
        }

    severity_level = result.severity.level

    if severity_level not in {"LOW", "MEDIUM", "HIGH"}:
        return {
            "recommendation": "NO_SPRAY",
            "reason": "INVALID_SEVERITY",
            "auto_permitted": False,
        }

    # Automatic spraying is permitted only for a valid
    # disease + valid severity.
    if mode == "AUTO":
        return {
            "recommendation": severity_level,
            "reason": "SEVERITY_BASED",
            "auto_permitted": True,
        }

    # Manual mode never automatically activates the pump.
    return {
        "recommendation": severity_level,
        "reason": "SEVERITY_BASED",
        "auto_permitted": False,
    }