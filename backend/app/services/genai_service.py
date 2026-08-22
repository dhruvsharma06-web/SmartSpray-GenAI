"""Gemini-backed, read-only plant analysis for the demo assist endpoint."""

import json
import logging
from typing import Any

from pydantic import BaseModel, Field

from app.core.config import settings

logger = logging.getLogger(__name__)


class GenAIConfigurationError(RuntimeError):
    """Raised when the optional Gemini integration is not configured."""


class _NamedConfidence(BaseModel):
    name: str
    confidence: float = Field(ge=0, le=1)


class _Disease(_NamedConfidence):
    consistent_with_existing_detection: bool


class _Severity(BaseModel):
    percentage: float | None = Field(ge=0, le=100, default=None)
    level: str


class _Treatment(BaseModel):
    recommendation: str
    options: list[str]
    reason: str


class AssistResponse(BaseModel):
    """The public JSON contract returned by the Gemini assist endpoint."""

    plant: _NamedConfidence
    disease: _Disease
    severity: _Severity
    ai_analysis: str
    treatment: _Treatment
    warnings: list[str]


class GenAIService:
    """Keep Gemini integration isolated from detection and spray control."""

    def is_configured(self) -> bool:
        return bool(settings.gemini_api_key.strip())

    def analyze_image(
        self,
        image_bytes: bytes,
        mime_type: str,
        detection_context: dict[str, Any],
    ) -> dict[str, Any]:
        """Request a constrained JSON advisory response from Gemini.

        This method deliberately returns recommendations only. It never imports or
        calls hardware or spray services.
        """
        if not self.is_configured():
            raise GenAIConfigurationError(
                "Gemini is not configured. Set GEMINI_API_KEY to enable /ai/assist."
            )

        # Import lazily so deployments without this optional feature can still run.
        from google import genai
        from google.genai import types

        prompt = """You are SmartSpray's plant-care demo assistant. Analyze the supplied plant image and the existing local detection context below. Return JSON only, with exactly this shape:
{
  "plant": {"name": string, "confidence": number},
  "disease": {"name": string, "confidence": number, "consistent_with_existing_detection": boolean},
  "severity": {"percentage": number|null, "level": string},
  "ai_analysis": string,
  "treatment": {"recommendation": string, "options": [string], "reason": string},
  "warnings": [string]
}

Use the image as the primary source for crop and disease identification. Treat local detection as context, not fact. Be transparent about uncertainty. This is a demonstration, not a diagnosis. Give general integrated-pest-management and label-following treatment guidance only. Never invent pesticide names, dosages, dilution ratios, application rates, or timing. Do not instruct any pump, device, or spraying action. Include a warning to follow local product labels and consult a qualified agronomist when appropriate.

Existing local detection context:
""" + json.dumps(detection_context, ensure_ascii=False)

        client = genai.Client(api_key=settings.gemini_api_key)
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=[prompt, types.Part.from_bytes(data=image_bytes, mime_type=mime_type)],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AssistResponse,
            ),
        )
        if not response.text:
            raise RuntimeError("Gemini returned an empty response")

        try:
            result = json.loads(response.text)
        except json.JSONDecodeError as exc:
            logger.warning("Gemini returned invalid JSON: %s", exc)
            raise RuntimeError("Gemini returned an invalid structured response") from exc

        if not isinstance(result, dict):
            raise RuntimeError("Gemini returned an invalid structured response")
        try:
            return AssistResponse.model_validate(result).model_dump()
        except ValueError as exc:
            logger.warning("Gemini response did not match assist contract: %s", exc)
            raise RuntimeError("Gemini returned an invalid structured response") from exc


genai_service = GenAIService()
