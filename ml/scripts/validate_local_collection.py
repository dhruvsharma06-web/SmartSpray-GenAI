"""Validate a local SmartSpray webcam collection manifest and labels."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}
SPLITS = {"train", "val", "test", "evaluation"}
REQUIRED_FIELDS = {
    "capture_id",
    "plant_id",
    "leaf_id",
    "session_id",
    "split",
    "image_path",
    "annotation_path",
    "label_state",
    "lighting",
    "distance_cm",
    "angle_deg",
}
LABEL_STATES = {"healthy_looking", "lesion_present", "uncertain"}


def _error(errors: list[str], row_number: int, message: str) -> None:
    errors.append(f"row {row_number}: {message}")


def validate_collection(manifest_path: Path) -> dict[str, object]:
    errors: list[str] = []
    rows: list[dict[str, str]] = []
    try:
        with manifest_path.open("r", newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            fields = set(reader.fieldnames or [])
            missing_fields = sorted(REQUIRED_FIELDS - fields)
            if missing_fields:
                errors.append(f"missing required fields: {', '.join(missing_fields)}")
            rows = list(reader)
    except OSError as exc:
        return {"valid": False, "errors": [str(exc)], "rows": 0}

    ids: set[str] = set()
    identities: dict[str, set[str]] = defaultdict(set)
    plants_by_split: dict[str, set[str]] = defaultdict(set)
    split_counts: dict[str, int] = defaultdict(int)
    for row_number, row in enumerate(rows, start=2):
        capture_id = row.get("capture_id", "").strip()
        plant_id = row.get("plant_id", "").strip()
        leaf_id = row.get("leaf_id", "").strip()
        session_id = row.get("session_id", "").strip()
        split = row.get("split", "").strip().lower()
        state = row.get("label_state", "").strip().lower()
        image_path = Path(row.get("image_path", "").strip())
        annotation_value = row.get("annotation_path", "").strip()

        if capture_id in ids and capture_id:
            _error(errors, row_number, f"duplicate capture_id: {capture_id}")
        ids.add(capture_id)
        for field, value in (("capture_id", capture_id), ("plant_id", plant_id), ("leaf_id", leaf_id), ("session_id", session_id)):
            if not value:
                _error(errors, row_number, f"{field} is required")
        if split not in SPLITS:
            _error(errors, row_number, f"split must be one of {sorted(SPLITS)}")
        if state not in LABEL_STATES:
            _error(errors, row_number, f"label_state must be one of {sorted(LABEL_STATES)}")
        if image_path.suffix.lower() not in IMAGE_SUFFIXES:
            _error(errors, row_number, "image_path must point to a JPG, JPEG, or PNG")
        if not annotation_value:
            _error(errors, row_number, "annotation_path is required; healthy samples use an empty label file")
        if state == "healthy_looking" and annotation_value and not annotation_value.lower().endswith(".txt"):
            _error(errors, row_number, "healthy_looking annotation_path must be an empty Ultralytics .txt label file")
        if state == "lesion_present" and annotation_value and not annotation_value.lower().endswith(".txt"):
            _error(errors, row_number, "lesion_present annotation_path must be an Ultralytics .txt label file")
        try:
            distance = float(row.get("distance_cm", ""))
            angle = float(row.get("angle_deg", ""))
            if distance <= 0:
                _error(errors, row_number, "distance_cm must be positive")
            if not -180 <= angle <= 180:
                _error(errors, row_number, "angle_deg must be between -180 and 180")
        except ValueError:
            _error(errors, row_number, "distance_cm and angle_deg must be numeric")

        split_counts[split] += 1
        if split in SPLITS and leaf_id and session_id:
            identities[f"leaf:{leaf_id}"].add(split)
            identities[f"session:{session_id}"].add(split)
        if split in SPLITS and plant_id:
            plants_by_split[split].add(plant_id)

    for identity, used_splits in identities.items():
        if len(used_splits) > 1:
            errors.append(f"identity {identity} appears in multiple splits: {sorted(used_splits)}")

    evaluation_plants = plants_by_split.get("evaluation", set())
    for split, plants in plants_by_split.items():
        if split != "evaluation":
            for plant_id in sorted(evaluation_plants & plants):
                errors.append(f"plant:{plant_id} appears in evaluation and {split}")

    return {
        "valid": not errors,
        "errors": errors,
        "rows": len(rows),
        "split_counts": dict(sorted(split_counts.items())),
        "plants": len({row.get("plant_id", "").strip() for row in rows if row.get("plant_id", "").strip()}),
        "leaves": len({row.get("leaf_id", "").strip() for row in rows if row.get("leaf_id", "").strip()}),
        "sessions": len({row.get("session_id", "").strip() for row in rows if row.get("session_id", "").strip()}),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    report = validate_collection(args.manifest)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["valid"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
