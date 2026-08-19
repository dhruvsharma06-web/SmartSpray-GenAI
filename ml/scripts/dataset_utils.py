"""Schema-tolerant PlantSeg audit and Ultralytics-segmentation helpers.

The scripts intentionally discover a local PlantSeg release instead of encoding an
unverified release layout.  They support the published image + grayscale-mask
layout once metadata maps each image to its mask.
"""

from __future__ import annotations

import csv
import hashlib
import json
import random
import shutil
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import Any, Iterable

import numpy as np
from PIL import Image, UnidentifiedImageError

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
METADATA_NAMES = ("Metadata.csv", "metadata.csv", "metadata/Metadata.csv")
IMAGE_FIELDS = ("image_path", "image", "image_name", "filename", "file_name")
MASK_FIELDS = ("annotation_path", "annotation", "mask_path", "mask", "label_path")
HOST_FIELDS = ("plant_host", "host", "crop", "plant", "species")
DISEASE_FIELDS = ("disease_type", "disease", "disease_name", "condition", "class")
ID_FIELDS = ("image_id", "id", "image_name", "filename", "file_name")
GROUP_FIELDS = ("source_url", "source", "original_image", "original_id", "leaf_id", "session_id")
MASK_VALUE_FIELDS = ("mask_value", "label_value", "class_id", "disease_id", "annotation_value")


class DatasetSetupError(RuntimeError):
    """Raised when a local dataset cannot be inspected safely."""


@dataclass(frozen=True)
class Sample:
    identifier: str
    image_path: Path
    mask_path: Path | None
    host: str
    disease: str
    group: str
    mask_value: int | None = None


def normalise(value: str | None) -> str:
    return " ".join((value or "").replace("_", " ").replace("-", " ").lower().split())


def find_metadata(source: Path) -> Path:
    for relative in METADATA_NAMES:
        candidate = source / relative
        if candidate.is_file():
            return candidate
    matches = sorted(source.rglob("[Mm]etadata.csv"))
    if matches:
        return matches[0]
    raise DatasetSetupError(
        f"No metadata CSV found under {source}. Expected a PlantSeg release with "
        "Metadata.csv (or provide a release with image/mask metadata)."
    )


def _field(row: dict[str, str], candidates: Iterable[str]) -> str:
    lookup = {normalise(key): value for key, value in row.items()}
    for candidate in candidates:
        if normalise(candidate) in lookup:
            return lookup[normalise(candidate)] or ""
    return ""


def _resolve_path(source: Path, value: str, fallback_dirs: tuple[str, ...]) -> Path | None:
    if not value:
        return None
    supplied = Path(value)
    candidates = [supplied] if supplied.is_absolute() else [source / supplied]
    candidates.extend(source / directory / supplied.name for directory in fallback_dirs)
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    return candidates[0].resolve() if candidates else None


def load_samples(source: Path) -> tuple[list[Sample], list[str]]:
    metadata = find_metadata(source)
    with metadata.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise DatasetSetupError(f"Metadata file is empty or has no header: {metadata}")
        rows = list(reader)
        columns = list(reader.fieldnames)

    samples: list[Sample] = []
    for index, row in enumerate(rows, start=2):
        image_value = _field(row, IMAGE_FIELDS)
        identifier = _field(row, ID_FIELDS) or image_value or f"metadata_row_{index}"
        image_path = _resolve_path(source, image_value, ("images", "image"))
        mask_path = _resolve_path(source, _field(row, MASK_FIELDS), ("annotations", "annotation", "masks", "labels"))
        group = _field(row, GROUP_FIELDS) or identifier
        raw_mask_value = _field(row, MASK_VALUE_FIELDS)
        try:
            mask_value = int(raw_mask_value) if raw_mask_value else None
        except ValueError:
            mask_value = None
        samples.append(Sample(identifier, image_path or source / "__missing__", mask_path, _field(row, HOST_FIELDS), _field(row, DISEASE_FIELDS), group, mask_value))
    return samples, columns


def inspect_mask(mask_path: Path) -> tuple[np.ndarray | None, str | None]:
    try:
        with Image.open(mask_path) as image:
            data = np.asarray(image.convert("L"))
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        return None, str(exc)
    if data.ndim != 2 or data.size == 0:
        return None, "mask is empty or not a single-channel raster"
    return data, None


def lesion_mask(mask: np.ndarray, mask_value: int | None) -> np.ndarray:
    """Choose a target label safely, refusing ambiguous multi-label masks."""
    values = [int(value) for value in np.unique(mask) if int(value) != 0]
    if mask_value is not None:
        if mask_value not in values:
            raise ValueError(f"declared mask value {mask_value} is not present")
        return (mask == mask_value).astype(np.uint8)
    if len(values) != 1:
        raise ValueError("ambiguous multi-label mask: metadata must declare the target mask value")
    return (mask == values[0]).astype(np.uint8)


def image_size(path: Path) -> tuple[int, int]:
    with Image.open(path) as image:
        image.verify()
    with Image.open(path) as image:
        return image.size


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def mask_to_polygons(mask: np.ndarray, width: int, height: int) -> list[list[float]]:
    """Convert non-zero connected mask regions to normalized exterior polygons."""
    if mask.shape != (height, width):
        raise ValueError(f"mask dimensions {mask.shape[::-1]} do not match image {(width, height)}")
    binary = (mask > 0).astype(np.uint8)
    contours = _contours(binary)
    polygons: list[list[float]] = []
    for contour in contours:
        if len(contour) < 3:
            continue
        points = np.asarray(contour).reshape(-1, 2)
        polygon = [coordinate for x, y in points for coordinate in (x / width, y / height)]
        if len(polygon) >= 6:
            polygons.append(polygon)
    return polygons


def _contours(binary: np.ndarray) -> list[np.ndarray]:
    """Find external contours, using OpenCV when available.

    OpenCV is supplied by the backend runtime.  The compact fallback keeps the
    audit/conversion utilities testable in a bare Python environment; it emits a
    convex exterior around each connected region rather than silently failing.
    """
    try:
        import cv2  # type: ignore
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return list(contours)
    except ImportError:
        pass
    visited = np.zeros_like(binary, dtype=bool)
    contours: list[np.ndarray] = []
    height, width = binary.shape
    for y, x in zip(*np.where(binary & ~visited)):
        if visited[y, x]:
            continue
        stack, component = [(int(y), int(x))], []
        visited[y, x] = True
        while stack:
            cy, cx = stack.pop(); component.append((cy, cx))
            for dy, dx in ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)):
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < height and 0 <= nx < width and binary[ny, nx] and not visited[ny, nx]:
                    visited[ny, nx] = True; stack.append((ny, nx))
        boundary = [(py, px) for py, px in component if any(py + dy < 0 or py + dy >= height or px + dx < 0 or px + dx >= width or not binary[py + dy, px + dx] for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)))]
        if len(boundary) < 3:
            continue
        cy, cx = np.mean([point[0] for point in boundary]), np.mean([point[1] for point in boundary])
        boundary.sort(key=lambda point: np.arctan2(point[0] - cy, point[1] - cx))
        contours.append(np.asarray([[[px, py]] for py, px in boundary], dtype=np.int32))
    return contours


def polygon_area_pixels(polygon: list[float], width: int, height: int) -> float:
    points = np.asarray(polygon, dtype=float).reshape(-1, 2)
    points[:, 0] *= width; points[:, 1] *= height
    return abs(float(np.dot(points[:, 0], np.roll(points[:, 1], -1)) - np.dot(points[:, 1], np.roll(points[:, 0], -1)))) / 2


def validate_polygon(polygon: list[float]) -> str | None:
    if len(polygon) < 6 or len(polygon) % 2:
        return "polygon must contain at least three x/y coordinate pairs"
    if any(not 0.0 <= coordinate <= 1.0 for coordinate in polygon):
        return "polygon coordinates must be normalized within [0, 1]"
    return None


def deterministic_split(samples: list[Sample], seed: int = 42) -> dict[str, list[Sample]]:
    """Assign whole source groups to a deterministic 70/15/15 split."""
    groups: dict[str, list[Sample]] = {}
    for sample in samples:
        groups.setdefault(sample.group or sample.identifier, []).append(sample)
    ordered = list(groups.items())
    random.Random(seed).shuffle(ordered)
    total = len(samples)
    targets = {"train": total * 0.70, "val": total * 0.15, "test": total * 0.15}
    result = {"train": [], "val": [], "test": []}
    for _, group_samples in ordered:
        split = min(result, key=lambda name: (abs(len(result[name]) + len(group_samples) - targets[name]), len(result[name])))
        result[split].extend(group_samples)
    return result


def audit_source(source: Path, target_host: str = "tomato", target_disease: str = "early blight") -> dict[str, Any]:
    samples, columns = load_samples(source)
    ids = Counter(sample.identifier for sample in samples)
    duplicate_ids = sorted(identifier for identifier, count in ids.items() if count > 1)
    hosts = Counter(sample.host for sample in samples if sample.host)
    diseases = Counter(sample.disease for sample in samples if sample.disease)
    target = [sample for sample in samples if normalise(sample.host) == normalise(target_host) and normalise(sample.disease) == normalise(target_disease)]
    missing_images = [sample.identifier for sample in samples if not sample.image_path.is_file()]
    total_annotations = sum(sample.mask_path is not None and sample.mask_path.is_file() for sample in samples)
    malformed_masks: dict[str, str] = {}
    target_malformed_masks: dict[str, str] = {}
    usable_masks = 0
    annotation_count = 0
    mask_values: Counter[int] = Counter()
    for sample in samples:
        if sample.mask_path and sample.mask_path.is_file():
            mask, error = inspect_mask(sample.mask_path)
            if error:
                malformed_masks[sample.identifier] = error
                if sample in target:
                    target_malformed_masks[sample.identifier] = error
            elif mask is not None and sample in target:
                annotation_count += 1
                mask_values.update(int(value) for value in np.unique(mask))
                try:
                    selected = lesion_mask(mask, sample.mask_value)
                except ValueError as exc:
                    malformed_masks[sample.identifier] = str(exc)
                    target_malformed_masks[sample.identifier] = str(exc)
                    continue
                if np.any(selected):
                    usable_masks += 1
        elif sample in target:
            malformed_masks[sample.identifier] = "missing annotation"
            target_malformed_masks[sample.identifier] = "missing annotation"
    return {
        "source": str(source.resolve()), "metadata_columns": columns,
        "total_images": len(samples), "total_annotations": total_annotations, "total_annotations_for_target": annotation_count,
        "host_categories": dict(sorted(hosts.items())), "disease_categories": dict(sorted(diseases.items())),
        "target": {"host": target_host, "disease": target_disease, "matching_images": len(target), "usable_masks": usable_masks},
        "missing_images": sorted(missing_images), "malformed_annotations": malformed_masks,
        "target_malformed_annotations": target_malformed_masks,
        "duplicate_identifiers": duplicate_ids, "target_mask_values": dict(sorted(mask_values.items())),
    }


def copy_and_convert(samples_by_split: dict[str, list[Sample]], output: Path, manifests: Path) -> dict[str, Any]:
    stats: dict[str, Any] = {"splits": {}, "invalid_samples": {}}
    dimensions: list[tuple[int, int]] = []
    areas: list[int] = []
    for split, samples in samples_by_split.items():
        image_dir, label_dir = output / "images" / split, output / "labels" / split
        image_dir.mkdir(parents=True, exist_ok=True); label_dir.mkdir(parents=True, exist_ok=True)
        manifest_lines: list[str] = []
        masks = 0
        for sample in samples:
            try:
                width, height = image_size(sample.image_path)
                mask, error = inspect_mask(sample.mask_path) if sample.mask_path else (None, "missing annotation")
                if error or mask is None:
                    raise ValueError(error or "missing annotation")
                polygons = mask_to_polygons(lesion_mask(mask, sample.mask_value), width, height)
                if not polygons:
                    raise ValueError("annotation contains no positive polygon")
                destination = image_dir / sample.image_path.name
                if destination.exists() and file_hash(destination) != file_hash(sample.image_path):
                    raise ValueError("duplicate image filename has different content")
                shutil.copy2(sample.image_path, destination)
                lines = []
                for polygon in polygons:
                    invalid = validate_polygon(polygon)
                    if invalid:
                        raise ValueError(invalid)
                    lines.append("0 " + " ".join(f"{point:.6f}" for point in polygon))
                (label_dir / f"{destination.stem}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
                manifest_lines.append(str(destination.resolve()))
                dimensions.append((width, height)); areas.extend(int(polygon_area_pixels(p, width, height)) for p in polygons)
                masks += len(polygons)
            except (OSError, UnidentifiedImageError, ValueError) as exc:
                stats["invalid_samples"][sample.identifier] = str(exc)
        manifests.mkdir(parents=True, exist_ok=True)
        (manifests / f"{split}.txt").write_text("\n".join(manifest_lines) + ("\n" if manifest_lines else ""), encoding="utf-8")
        stats["splits"][split] = {"samples": len(manifest_lines), "lesion_masks": masks}
    widths, heights = zip(*dimensions) if dimensions else ([], [])
    stats["image_dimensions"] = {"minimum": [min(widths), min(heights)] if widths else None, "maximum": [max(widths), max(heights)] if widths else None, "median": [median(widths), median(heights)] if widths else None}
    stats["mask_area_pixels"] = {"minimum": min(areas) if areas else None, "median": median(areas) if areas else None, "maximum": max(areas) if areas else None}
    return stats


def dump_json(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True)
