"""Lazy, one-time Ultralytics YOLO model loading."""

import logging
from pathlib import Path
from typing import Any, Callable

from app.ai.errors import ModelLoadError
from app.core.config import settings

logger = logging.getLogger(__name__)


class ModelLoader:
    """Loads local YOLO weights once and exposes readiness/metadata."""

    def __init__(
        self,
        model_path: str | None = None,
        device: str | None = None,
        model_factory: Callable[..., Any] | None = None,
    ):
        self.model_path = Path(model_path or settings.ai_model_path)
        self.requested_device = device or settings.ai_device
        self._model_factory = model_factory
        self._model: Any | None = None
        self._load_error: str | None = None
        self._resolved_device: str | None = None

    @property
    def ready(self) -> bool:
        return self._model is not None

    @property
    def load_error(self) -> str | None:
        return self._load_error

    @property
    def resolved_device(self) -> str | None:
        return self._resolved_device

    @property
    def model(self) -> Any:
        if not self.ready:
            self.load()
        return self._model

    @property
    def class_names(self) -> dict[int, str] | list[str] | None:
        if not self.ready:
            return None
        return getattr(self._model, "names", None)

    def load(self) -> Any:
        """Load weights once; never download or replace missing weights."""
        if self.ready:
            return self._model
        if not self.model_path.is_file():
            self._load_error = "Model weights are missing"
            logger.error("Model initialization failed: weights unavailable")
            raise ModelLoadError(self._load_error)

        self._resolved_device = self._resolve_device()
        try:
            factory = self._model_factory or self._default_factory()
            self._model = factory(str(self.model_path))
            if hasattr(self._model, "to"):
                self._model.to(self._resolved_device)
            self._load_error = None
            logger.info("Model initialized")
            return self._model
        except ModelLoadError:
            raise
        except Exception as exc:
            self._load_error = "Model initialization failed"
            logger.error("Model initialization failed: %s", exc)
            raise ModelLoadError(self._load_error) from exc

    def _resolve_device(self) -> str:
        if self.requested_device and self.requested_device != "auto":
            return self.requested_device
        try:
            import torch
            return "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            return "cpu"

    @staticmethod
    def _default_factory() -> Callable[..., Any]:
        try:
            from ultralytics import YOLO
        except ImportError as exc:
            raise ModelLoadError("Ultralytics is not installed") from exc
        return YOLO
