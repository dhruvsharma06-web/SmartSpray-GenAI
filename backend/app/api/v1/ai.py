"""Minimal AI readiness endpoint."""

from fastapi import APIRouter

from app.ai.camera import Camera
from app.ai.model_loader import ModelLoader
from app.schemas.common import success_response

router = APIRouter(prefix="/ai", tags=["ai"])

_camera = Camera()
_model_loader = ModelLoader()


@router.get("/status")
async def get_ai_status():
    """Report readiness without opening hardware or loading weights."""
    camera_ready = _camera.is_open()
    model_ready = _model_loader.ready
    return success_response({
        "ready": camera_ready and model_ready,
        "camera": camera_ready,
        "model": model_ready,
    })
