"""AI-001 tests using fake camera and model objects only."""

import pytest

from app.ai.camera import Camera
from app.ai.detector import Detector
from app.ai.errors import DetectionError, ModelLoadError
from app.ai.model_loader import ModelLoader


class FakeCapture:
    def __init__(self, opened=True, reads=None):
        self.opened = opened
        self.reads = list(reads or [])
        self.released = False

    def isOpened(self):
        return self.opened and not self.released

    def read(self):
        if not self.reads:
            return False, None
        return self.reads.pop(0)

    def release(self):
        self.released = True


class FakeBoxes:
    def __init__(self, xyxy, conf, cls):
        self.xyxy = xyxy
        self.conf = conf
        self.cls = cls


class FakeResult:
    def __init__(self, boxes, names=None):
        self.boxes = boxes
        self.names = names or {0: "healthy", 1: "diseased"}


class FakeModel:
    def __init__(self, results):
        self.results = results
        self.calls = 0
        self.kwargs = None

    def predict(self, **kwargs):
        self.calls += 1
        self.kwargs = kwargs
        return self.results


def test_camera_open_read_and_release():
    capture = FakeCapture(reads=[(True, "frame")])
    camera = Camera(index=0, capture_factory=lambda index: capture)

    assert camera.open() is True
    assert camera.is_open() is True
    result = camera.read()
    assert result.ok is True
    assert result.frame == "frame"

    camera.release()
    assert camera.is_open() is False
    assert capture.released is True


def test_camera_unavailable_and_failed_frame():
    unavailable = FakeCapture(opened=False)
    camera = Camera(index=0, capture_factory=lambda index: unavailable)
    assert camera.open() is False
    assert camera.last_error == "Camera is unavailable"

    failed_capture = FakeCapture(reads=[(False, None)])
    camera = Camera(index=0, capture_factory=lambda index: failed_capture)
    assert camera.open() is True
    result = camera.read()
    assert result.ok is False
    assert result.error == "FRAME_CAPTURE_FAILED"


def test_camera_invalid_index_and_unopened_read():
    camera = Camera(index=-1, capture_factory=lambda index: FakeCapture())
    assert camera.open() is False
    assert camera.read().error == "CAMERA_NOT_OPEN"


def test_model_loader_missing_weights():
    loader = ModelLoader(model_path="missing-weights.pt")
    with pytest.raises(ModelLoadError, match="weights are missing"):
        loader.load()
    assert loader.ready is False


def test_model_loader_loads_once_and_uses_cpu_fallback(tmp_path):
    weights = tmp_path / "model.pt"
    weights.write_bytes(b"test")
    model = FakeModel([])
    calls = []
    loader = ModelLoader(
        model_path=str(weights),
        device="cpu",
        model_factory=lambda path: calls.append(path) or model,
    )

    assert loader.load() is model
    assert loader.load() is model
    assert calls == [str(weights)]
    assert loader.ready is True
    assert loader.resolved_device == "cpu"


def test_detector_valid_detection_and_model_call():
    model = FakeModel([
        FakeResult(FakeBoxes([[10, 20, 30, 50]], [0.91], [1]))
    ])
    detector = Detector(model=model, confidence_threshold=0.5)

    result = detector.detect("frame")

    assert result.detected is True
    assert result.class_name == "diseased"
    assert result.confidence == pytest.approx(0.91)
    assert result.bounding_box.width == 20
    assert result.bounding_box.height == 30
    assert result.uncertainty is False
    assert len(result.detections) == 1
    assert model.calls == 1
    assert model.kwargs["conf"] == 0.0


def test_detector_low_confidence_is_uncertain_and_retains_raw_value():
    model = FakeModel([
        FakeResult(FakeBoxes([[0, 0, 10, 10]], [0.4], [1]))
    ])

    result = Detector(model=model, confidence_threshold=0.5).detect("frame")

    assert result.detected is False
    assert result.uncertainty is True
    assert result.confidence == pytest.approx(0.4)
    assert result.detections[0].class_name == "diseased"


def test_detector_no_detection():
    model = FakeModel([FakeResult(FakeBoxes([], [], []))])

    result = Detector(model=model).detect("frame")

    assert result.detected is False
    assert result.uncertainty is False
    assert result.detections == []


def test_detector_multiple_detections():
    model = FakeModel([
        FakeResult(FakeBoxes(
            [[0, 0, 10, 10], [20, 20, 50, 60]],
            [0.6, 0.95],
            [0, 1],
        ))
    ])

    result = Detector(model=model, confidence_threshold=0.5).detect("frame")

    assert result.detected is True
    assert len(result.detections) == 2
    assert result.class_name == "diseased"


def test_detector_rejects_malformed_model_result():
    model = FakeModel([object()])

    with pytest.raises(DetectionError, match="no boxes"):
        Detector(model=model).detect("frame")


@pytest.mark.anyio
async def test_ai_status_does_not_open_camera_or_load_model(client):
    response = await client.get("/api/v1/ai/status")

    assert response.status_code == 200
    assert response.json()["data"]["ready"] is False
    assert "leaf_model" in response.json()["data"]
