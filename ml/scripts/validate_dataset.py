"""Validate generated Ultralytics segmentation images, labels, and manifests."""
from __future__ import annotations
import argparse
import sys
from collections import Counter
from pathlib import Path
from dataset_utils import IMAGE_SUFFIXES, file_hash, image_size, validate_polygon, dump_json

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument("--dataset", type=Path, default=Path("ml/datasets/processed/plantseg_tomato_early_blight")); parser.add_argument("--manifests", type=Path, default=Path("ml/datasets/manifests")); args = parser.parse_args()
    problems: dict[str, str] = {}; hashes: Counter[str] = Counter(); total = 0; empty_annotations: list[str] = []; manifest_problems: dict[str, str] = {}
    for split in ("train", "val", "test"):
        image_paths = [path for path in sorted((args.dataset / "images" / split).glob("*")) if path.suffix.lower() in IMAGE_SUFFIXES] if (args.dataset / "images" / split).is_dir() else []
        manifest = args.manifests / f"{split}.txt"
        if not manifest.is_file():
            manifest_problems[split] = "missing manifest"
        else:
            expected = {str(path.resolve()) for path in image_paths}
            actual = {line.strip() for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()}
            if actual != expected:
                manifest_problems[split] = "manifest entries do not match generated images"
        for image_path in image_paths:
            total += 1; label = args.dataset / "labels" / split / f"{image_path.stem}.txt"
            try:
                image_size(image_path); hashes[file_hash(image_path)] += 1
                if not label.is_file(): raise ValueError("missing annotation")
                lines = [line for line in label.read_text(encoding="utf-8").splitlines() if line.strip()]
                if not lines:
                    empty_annotations.append(str(image_path))
                for line in lines:
                    values = line.split()
                    if not values or values[0] != "0": raise ValueError("expected class 0")
                    invalid = validate_polygon([float(value) for value in values[1:]])
                    if invalid: raise ValueError(invalid)
            except (OSError, ValueError) as exc: problems[str(image_path)] = str(exc)
    report = {"total_samples": total, "invalid_samples": problems, "empty_annotations": empty_annotations, "manifest_problems": manifest_problems, "duplicate_images": sorted(key for key, count in hashes.items() if count > 1)}
    print(dump_json(report)); return 0 if not problems and not empty_annotations and not manifest_problems and not report["duplicate_images"] else 3

if __name__ == "__main__": raise SystemExit(main())
