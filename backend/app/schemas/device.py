"""Device-related schemas."""

from typing import Optional
from pydantic import BaseModel


class DeviceStatusResponse(BaseModel):
    device_uid: str
    status: str  # online/offline/error
    mode: str   # auto/assisted/manual
    firmware_version: Optional[str] = None
    is_spraying: bool = False
    is_emergency_stopped: bool = False
    pump_runtime_ms: Optional[int] = None


class SetModeRequest(BaseModel):
    mode: str  # auto/assisted/manual
