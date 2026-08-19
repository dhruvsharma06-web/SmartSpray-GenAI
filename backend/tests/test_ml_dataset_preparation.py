"""Synthetic-fixture tests for ML preparation; no PlantSeg download required."""
from __future__ import annotations
import importlib.util
import sys
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "ml" / "scripts"
sys.path.insert(0, str(SCRIPTS))
from dataset_utils import Sample, audit_source, copy_and_convert, deterministic_split, mask_to_polygons, validate_polygon

def _fixture(root: Path) -> Path:
    source = root / "plantseg"; (source / "images").mkdir(parents=True); (source / "annotations").mkdir()
    rows = ["image_id,image_path,annotation_path,plant_host,disease_type,source_url"]
    for index in range(4):
        image = np.full((10, 12, 3), 255, dtype=np.uint8); image[0, 0] = index; Image.fromarray(image).save(source / "images" / f"{index}.png")
        mask = np.zeros((10, 12), dtype=np.uint8); mask[2:7, 3:9] = 1; Image.fromarray(mask).save(source / "annotations" / f"{index}.png")
        rows.append(f"id{index},images/{index}.png,annotations/{index}.png,tomato,early blight,leaf-{index // 2}")
    (source / "Metadata.csv").write_text("\n".join(rows) + "\n", encoding="utf-8"); return source

def test_audit_counts_target_and_masks(tmp_path):
    report = audit_source(_fixture(tmp_path))
    assert report["target"]["matching_images"] == 4
    assert report["target"]["usable_masks"] == 4
    assert report["missing_images"] == []

def test_polygon_conversion_is_normalized_and_rejects_invalid_values():
    mask = np.zeros((10, 10), dtype=np.uint8); mask[2:8, 2:8] = 1
    polygon = mask_to_polygons(mask, 10, 10)[0]
    assert validate_polygon(polygon) is None
    assert validate_polygon([1.1, 0, 0, 1, 0, 0])

def test_split_is_deterministic_and_keeps_groups_together():
    samples = [Sample(str(i), Path(f"{i}.png"), None, "tomato", "early blight", f"leaf-{i // 2}") for i in range(10)]
    first, second = deterministic_split(samples, 7), deterministic_split(samples, 7)
    assert {key: [s.identifier for s in value] for key, value in first.items()} == {key: [s.identifier for s in value] for key, value in second.items()}
    assigned = {sample.group: split for split, values in first.items() for sample in values}
    assert len(assigned) == 5

def test_conversion_writes_manifests_and_validation_ready_labels(tmp_path):
    source = _fixture(tmp_path); report = audit_source(source)
    from dataset_utils import load_samples
    samples, _ = load_samples(source)
    stats = copy_and_convert(deterministic_split(samples), tmp_path / "processed", tmp_path / "manifests")
    assert sum(split["samples"] for split in stats["splits"].values()) == 4
    assert (tmp_path / "manifests" / "train.txt").exists()

def test_audit_detects_duplicate_identifiers(tmp_path):
    source = _fixture(tmp_path)
    metadata = source / "Metadata.csv"
    metadata.write_text(metadata.read_text(encoding="utf-8") + "id0,images/1.png,annotations/1.png,tomato,early blight,leaf-extra\n", encoding="utf-8")
    assert audit_source(source)["duplicate_identifiers"] == ["id0"]

def test_generated_dataset_passes_validator(tmp_path, monkeypatch):
    source = _fixture(tmp_path)
    from dataset_utils import load_samples
    samples, _ = load_samples(source)
    processed, manifests = tmp_path / "processed", tmp_path / "manifests"
    copy_and_convert(deterministic_split(samples), processed, manifests)
    from validate_dataset import main
    monkeypatch.setattr(sys, "argv", ["validate_dataset.py", "--dataset", str(processed), "--manifests", str(manifests)])
    assert main() == 0
