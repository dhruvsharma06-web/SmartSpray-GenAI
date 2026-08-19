"""Spray-related request/response schemas."""

from typing import Optional
from pydantic import BaseModel, Field


class ManualSprayRequest(BaseModel):
    device_id: str
    servo_angle: int = Field(ge=0, le=180)
    duration_ms: int = Field(ge=0, le=10000)
    command_id: Optional[str] = None


class StopRequest(BaseModel):
    device_id: str


class SprayEventResponse(BaseModel):
    id: int
    mode: str
    servo_angle: int
    duration_ms: int
    status: str
    command_id: Optional[str] = None
    error_message: Optional[str] = None
    started_at: str
    completed_at: Optional[str] = None


class SprayHistoryItem(BaseModel):
    id: int
    device_id: str
    mode: str
    servo_angle: int
    duration_ms: int
    status: str
    command_id: Optional[str] = None
    error_message: Optional[str] = None
    started_at: str
    completed_at: Optional[str] = None
