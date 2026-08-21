"""Minimal AI readiness endpoint."""
import threading
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException
import cv2
import numpy as np
from app.services.ai_service import ai_service
from app.schemas.common import success_response, error_response

router = APIRouter(prefix="/ai", tags=["ai"])

# Guard against concurrent webcam access — only one /detect request
# may hold the camera at a time.
_camera_lock = threading.Lock()

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
