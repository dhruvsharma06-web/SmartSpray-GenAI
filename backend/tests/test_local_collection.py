"""Synthetic tests for the AI-003 local collection manifest validator."""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "ml" / "scripts"))
from validate_local_collection import validate_collection


def _write_manifest(path: Path, rows: list[dict[str, str]]) -> Path:
    fields = [
        "capture_id", "plant_id", "leaf_id", "session_id", "split",
        "image_path", "annotation_path", "label_state", "distance_cm",
        "angle_deg", "lighting", "occlusion", "notes",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    return path


def _row(capture: str, leaf: str, split: str, state: str = "lesion_present") -> dict[str, str]:
    return {
        "capture_id": capture,
        "plant_id": "plant-001",
        "leaf_id": leaf,
        "session_id": f"session-{leaf}",
        "split": split,
        "image_path": f"images/{split}/{capture}.jpg",
        "annotation_path": f"labels/{split}/{capture}.txt",
        "label_state": state,
        "distance_cm": "40",
        "angle_deg": "0",
        "lighting": "diffuse",
        "occlusion": "none",
        "notes": "",
    }


def test_valid_collection_manifest_reports_identity_counts(tmp_path):
    rows = [
        _row("capture-train", "leaf-train", "train"),
        _row("capture-val", "leaf-val", "val"),
        _row("capture-eval", "leaf-eval", "evaluation"),
    ]
    rows[0]["plant_id"], rows[1]["plant_id"], rows[2]["plant_id"] = "plant-001", "plant-002", "plant-003"
    manifest = _write_manifest(tmp_path / "metadata.csv", rows)

    report = validate_collection(manifest)

    assert report["valid"] is True
    assert report["rows"] == 3
    assert report["plants"] == 3
    assert report["leaves"] == 3
    assert report["sessions"] == 3
    assert report["split_counts"] == {"evaluation": 1, "train": 1, "val": 1}


def test_leaf_and_session_leakage_across_splits_is_rejected(tmp_path):
    first = _row("capture-1", "leaf-shared", "train")
    second = _row("capture-2", "leaf-shared", "val")
    second["session_id"] = "session-other"
    manifest = _write_manifest(tmp_path / "metadata.csv", [first, second])

    report = validate_collection(manifest)

    assert report["valid"] is False
    assert any("leaf:leaf-shared" in error for error in report["errors"])


def test_duplicate_capture_id_is_rejected(tmp_path):
    manifest = _write_manifest(tmp_path / "metadata.csv", [
        _row("same-capture", "leaf-1", "train"),
        _row("same-capture", "leaf-2", "train"),
    ])

    report = validate_collection(manifest)

    assert report["valid"] is False
    assert any("duplicate capture_id" in error for error in report["errors"])


def test_healthy_looking_requires_empty_label_file(tmp_path):
    row = _row("healthy-capture", "leaf-healthy", "train", "healthy_looking")
    row["annotation_path"] = "labels/train/healthy-capture.png"
    manifest = _write_manifest(tmp_path / "metadata.csv", [row])

    report = validate_collection(manifest)

    assert report["valid"] is False
    assert any("empty Ultralytics .txt" in error for error in report["errors"])


def test_evaluation_plant_cannot_appear_in_training(tmp_path):
    evaluation = _row("eval-capture", "leaf-eval", "evaluation")
    training = _row("train-capture", "leaf-train", "train")
    training["plant_id"] = evaluation["plant_id"]
    manifest = _write_manifest(tmp_path / "metadata.csv", [evaluation, training])

    report = validate_collection(manifest)

    assert report["valid"] is False
    assert any("plant:plant-001" in error for error in report["errors"])
