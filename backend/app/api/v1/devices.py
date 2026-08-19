"""Device management API endpoints."""

from fastapi import APIRouter
from app.schemas.device import SetModeRequest
from app.schemas.common import success_response, error_response
from app.services.hardware_controller import hardware_controller

router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("/{device_id}/status")
async def get_device_status(device_id: str):
    """Get current device status including servo, pump, and safety state."""
    result = hardware_controller.get_status(device_id=device_id)
    return result


@router.post("/{device_id}/mode")
async def set_device_mode(device_id: str, request: SetModeRequest):
    """Set the device operating mode (auto/assisted/manual)."""
    result = hardware_controller.set_mode(request.mode, device_id=device_id)
    return result
