"""Train and evaluate the local YOLO11n-seg PlantSeg baseline."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import yaml


def _device() -> str:
    import torch
    return "0" if torch.cuda.is_available() else "cpu"


def _metric(metrics: Any, *names: str) -> float | None:
    for name in names:
        value = metrics.get(name) if isinstance(metrics, dict) else None
        if value is not None:
            return float(value)
        value = getattr(metrics, name, None)
        if value is not None:
            return float(value)
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("ml/configs/plantseg_tomato_early_blight.yaml"))
    parser.add_argument("--project", type=Path, default=Path("ml/runs"))
    parser.add_argument("--name", default="yolo11n_seg_plantseg")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", default=None, help="CUDA device index or cpu; defaults to CUDA when available")
    args = parser.parse_args()

    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise SystemExit("Ultralytics is required. Install the declared backend AI dependencies first.") from exc

    device = args.device or _device()
    dataset = yaml.safe_load(args.data.read_text(encoding="utf-8"))
    dataset_root = (args.data.parent / dataset["path"]).resolve()
    dataset["path"] = str(dataset_root)
    args.project = args.project.resolve()
    args.project.mkdir(parents=True, exist_ok=True)
    run_dir = args.project / args.name
    run_dir.mkdir(parents=True, exist_ok=True)
    resolved_data = run_dir / "resolved_dataset.yaml"
    resolved_data.write_text(yaml.safe_dump(dataset, sort_keys=False), encoding="utf-8")
    model = YOLO("yolo11n-seg.pt")
    started = time.perf_counter()
    model.train(
        data=str(resolved_data),
        imgsz=args.imgsz,
        epochs=args.epochs,
        batch=args.batch,
        seed=args.seed,
        device=device,
        patience=20,
        project=str(args.project),
        name=args.name,
        exist_ok=True,
        pretrained=True,
        fliplr=0.5,
        degrees=8.0,
        translate=0.05,
        scale=0.2,
        hsv_h=0.015,
        hsv_s=0.3,
        hsv_v=0.2,
        shear=0.0,
        perspective=0.0,
        mosaic=0.0,
        mixup=0.0,
    )
    best_path = args.project / args.name / "weights" / "best.pt"
    model = YOLO(str(best_path))
    validation = model.val(data=str(resolved_data), split="val", imgsz=args.imgsz, batch=args.batch, device=device, plots=True)
    test = model.val(data=str(resolved_data), split="test", imgsz=args.imgsz, batch=args.batch, device=device, plots=True)
    report = {
        "model": "YOLO11n-seg",
        "checkpoint": str(best_path),
        "device": device,
        "epochs": args.epochs,
        "batch": args.batch,
        "image_size": args.imgsz,
        "seed": args.seed,
        "training_seconds": round(time.perf_counter() - started, 2),
        "validation": {
            "map50": _metric(validation.box, "map50"),
            "map50_95": _metric(validation.box, "map"),
            "precision": _metric(validation.box, "mp"),
            "recall": _metric(validation.box, "mr"),
            "mask_map50": _metric(validation.seg, "map50"),
            "mask_map50_95": _metric(validation.seg, "map"),
        },
        "test": {
            "map50": _metric(test.box, "map50"),
            "map50_95": _metric(test.box, "map"),
            "precision": _metric(test.box, "mp"),
            "recall": _metric(test.box, "mr"),
            "mask_map50": _metric(test.seg, "map50"),
            "mask_map50_95": _metric(test.seg, "map"),
        },
        "mask_iou_dice": None,
    }
    report_path = args.project / args.name / "baseline_report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
