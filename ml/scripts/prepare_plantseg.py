"""Filter an audited GO PlantSeg subset and emit Ultralytics segmentation data."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path
from audit_plantseg import MINIMUM_USABLE_MASKS
from dataset_utils import DatasetSetupError, audit_source, copy_and_convert, deterministic_split, dump_json, load_samples, normalise

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("ml/datasets/raw/plantseg")); parser.add_argument("--output", type=Path, default=Path("ml/datasets/processed/plantseg_tomato_early_blight")); parser.add_argument("--manifests", type=Path, default=Path("ml/datasets/manifests")); parser.add_argument("--seed", type=int, default=42); parser.add_argument("--minimum-usable-masks", type=int, default=MINIMUM_USABLE_MASKS); parser.add_argument("--allow-baseline", action="store_true", help="Proceed for a documented baseline despite the normal GO/NO-GO gate; invalid samples remain excluded.")
    args = parser.parse_args()
    if not args.source.is_dir():
        print(f"SETUP REQUIRED: PlantSeg is not available at {args.source}. Run the audit only after placing an authorized local copy there. This script never downloads data.", file=sys.stderr)
        return 2
    try:
        audit = audit_source(args.source, target_disease="tomato early blight")
        if not args.allow_baseline and (audit["target"]["usable_masks"] < args.minimum_usable_masks or audit["target_malformed_annotations"]):
            print(dump_json({"gate": "NO-GO", "reason": "Target subset is below the usable-mask threshold or contains malformed target annotations.", "audit": audit}), file=sys.stderr); return 3
        samples, _ = load_samples(args.source)
    except DatasetSetupError as exc:
        print(f"SETUP REQUIRED: {exc}", file=sys.stderr); return 2
    target = [sample for sample in samples if normalise(sample.host) == "tomato" and normalise(sample.disease) == "tomato early blight"]
    stats = copy_and_convert(deterministic_split(target, args.seed), args.output, args.manifests)
    stats.update({"gate": "BASELINE_OVERRIDE" if args.allow_baseline else "GO", "seed": args.seed, "output": str(args.output), "target_samples": len(target), "audit": audit["target"]})
    print(dump_json(stats)); return 0

if __name__ == "__main__": raise SystemExit(main())
