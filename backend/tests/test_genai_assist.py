"""Contract tests for the optional, read-only Gemini assist endpoint."""

import numpy as np
import cv2
import pytest

from app.core.config import settings


def _image_bytes() -> bytes:
    ok, encoded = cv2.imencode(".jpg", np.zeros((16, 16, 3), dtype=np.uint8))
    assert ok
    return encoded.tobytes()


@pytest.mark.anyio
async def test_assist_reports_missing_gemini_configuration(client, monkeypatch):
    monkeypatch.setattr(settings, "gemini_api_key", "")

    response = await client.post(
        "/api/v1/ai/assist",
        files={"file": ("plant.jpg", _image_bytes(), "image/jpeg")},
    )

    assert response.status_code == 200
    assert response.json() == {
        "success": False,
        "error": {
            "code": "GENAI_NOT_CONFIGURED",
            "message": "Gemini is not configured. Set GEMINI_API_KEY to enable /api/v1/ai/assist.",
        },
    }


@pytest.mark.anyio
async def test_assist_rejects_invalid_image_before_calling_gemini(client, monkeypatch):
    monkeypatch.setattr(settings, "gemini_api_key", "test-key")

    response = await client.post(
        "/api/v1/ai/assist",
        files={"file": ("not-image.txt", b"not an image", "image/jpeg")},
    )

    assert response.status_code == 200
    assert response.json()["error"]["code"] == "INVALID_IMAGE"


@pytest.mark.anyio
async def test_assist_returns_gemini_structured_response(client, monkeypatch):
    from app.api.v1 import ai as ai_router

    expected = {
        "plant": {"name": "Tomato", "confidence": 0.91},
        "disease": {
            "name": "Early Blight",
            "confidence": 0.82,
            "consistent_with_existing_detection": True,
        },
        "severity": {"percentage": 57.8, "level": "MEDIUM"},
        "ai_analysis": "Leaf spots appear consistent with early blight.",
        "treatment": {
            "recommendation": "Remove affected foliage and consult the product label.",
            "options": ["Improve airflow"],
            "reason": "General demo guidance.",
        },
        "warnings": ["Follow local product labels."],
    }
    monkeypatch.setattr(settings, "gemini_api_key", "test-key")
    monkeypatch.setattr(ai_router, "_detection_context", lambda frame: {"available": True})
    monkeypatch.setattr(ai_router.genai_service, "analyze_image", lambda **kwargs: expected)

    response = await client.post(
        "/api/v1/ai/assist",
        files={"file": ("plant.jpg", _image_bytes(), "image/jpeg")},
    )

    assert response.status_code == 200
    assert response.json() == {"success": True, "data": expected}
