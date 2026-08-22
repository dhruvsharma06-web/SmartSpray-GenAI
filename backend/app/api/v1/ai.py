"""AI detection and read-only Gemini assist endpoints."""
import logging
import threading
from typing import Optional
from fastapi import APIRouter, UploadFile, File
import cv2
import numpy as np
from app.services.ai_service import ai_service
from app.services.genai_service import GenAIConfigurationError, genai_service
from app.schemas.common import success_response, error_response

router = APIRouter(prefix="/ai", tags=["ai"])
logger = logging.getLogger(__name__)

# Guard against concurrent webcam access — only one /detect request
# may hold the camera at a time.
_camera_lock = threading.Lock()


def _detection_context(frame: np.ndarray) -> dict:
    """Produce optional existing detector context without affecting assist availability."""
    result = ai_service.process_frame(frame)
    if "error" in result:
        return {"available": False, "error": result["error"]}

    data = result["data"]
    return {
        "available": True,
        "disease": data.get("disease"),
        "disease_confidence": (data.get("lesion") or {}).get("confidence"),
        "severity": data.get("severity"),
        "uncertain": data.get("uncertain", False),
    }

@router.get("/status")
async def get_ai_status():
    """Report readiness status of AI models."""
    status = ai_service.get_status()
    return success_response(status)

@router.post("/detect")
async def detect(file: Optional[UploadFile] = File(None)):
    if file is not None:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    else:
        # Capture from laptop webcam with guaranteed resource cleanup
        if not _camera_lock.acquire(blocking=False):
            return error_response(
                "CAMERA_BUSY",
                "Another detection request is already using the camera",
            )
        cap = None
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                return error_response(
                    "CAMERA_UNAVAILABLE",
                    "Cannot open camera — ensure no other application is using it",
                )
            ret, frame = cap.read()
            if not ret or frame is None:
                return error_response(
                    "FRAME_CAPTURE_FAILED",
                    "Camera opened but failed to capture a frame",
                )
        finally:
            if cap is not None:
                cap.release()
            _camera_lock.release()

    if frame is None:
        return error_response("INVALID_IMAGE", "Invalid image or capture failed.")

    result = ai_service.process_frame(frame)
    if "error" in result:
        return error_response(result["error"])

    return success_response({
        "success": True,
        "data": result["data"],
        "decision": result["decision"]
    })


@router.post("/assist")
async def assist(file: UploadFile = File(...)):
    """Return a Gemini-generated advisory; this endpoint cannot control spraying."""
    if not genai_service.is_configured():
        return error_response(
            "GENAI_NOT_CONFIGURED",
            "Gemini is not configured. Set GEMINI_API_KEY to enable /api/v1/ai/assist.",
        )

    image_bytes = await file.read()
    if not image_bytes:
        return error_response("INVALID_IMAGE", "The uploaded image is empty.")

    frame = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        return error_response("INVALID_IMAGE", "The uploaded file is not a valid image.")

    mime_type = file.content_type if file.content_type and file.content_type.startswith("image/") else "image/jpeg"
    try:
        analysis = genai_service.analyze_image(
            image_bytes=image_bytes,
            mime_type=mime_type,
            detection_context=_detection_context(frame),
        )
    except GenAIConfigurationError as exc:
        return error_response("GENAI_NOT_CONFIGURED", str(exc))
    except Exception:
        logger.exception("Gemini assist request failed")
        return error_response("GENAI_REQUEST_FAILED", "Gemini analysis is unavailable. Please try again later.")

    return success_response(analysis)
