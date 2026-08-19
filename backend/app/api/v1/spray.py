"""Spray control API endpoints."""

from fastapi import APIRouter
from app.schemas.spray import ManualSprayRequest, StopRequest
from app.schemas.common import success_response, error_response
from app.services.hardware_controller import hardware_controller

router = APIRouter(prefix="/spray", tags=["spray"])


@router.post("/manual")
async def manual_spray(request: ManualSprayRequest):
    """Execute a manual spray command.

    Validates all parameters through the full validation chain (Section 11)
    before sending to ESP32.
    """
    result = hardware_controller.manual_spray(
        device_id=request.device_id,
        servo_angle=request.servo_angle,
        duration_ms=request.duration_ms,
        command_id=request.command_id,
    )
    return result


@router.post("/stop")
async def stop_spray(request: StopRequest):
    """Stop any active spray operation."""
    result = hardware_controller.stop(device_id=request.device_id)
    return result


@router.post("/emergency-stop")
async def emergency_stop():
    """Software emergency stop — no confirmation dialog."""
    result = hardware_controller.emergency_stop()
    return result


@router.post("/reset-emergency-stop")
async def reset_emergency_stop():
    """Reset the software emergency stop."""
    result = hardware_controller.reset_emergency_stop()
    return result


@router.get("/history")
async def spray_history(device_id: str | None = None, limit: int = 50):
    """Return persisted spray events without serial protocol details."""
    limit = max(1, min(limit, 100))
    return success_response(hardware_controller.get_history(device_id=device_id, limit=limit))
