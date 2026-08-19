"""Common response schemas matching Section 12 API error format."""

from typing import Any, Optional
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: str
    message: str


class SuccessResponse(BaseModel):
    success: bool = True
    data: Any = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetail
    request_id: Optional[str] = None


def success_response(data: Any = None) -> dict:
    """Create a standard success response."""
    return {"success": True, "data": data}


def error_response(code: str, message: str, request_id: str | None = None) -> dict:
    """Create a standard error response."""
    resp = {
        "success": False,
        "error": {"code": code, "message": message},
    }
    if request_id:
        resp["request_id"] = request_id
    return resp
