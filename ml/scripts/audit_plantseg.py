"""Audit a locally supplied PlantSeg release; it never downloads data."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path
from dataset_utils import DatasetSetupError, audit_source, dump_json

MINIMUM_USABLE_MASKS = 300

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("ml/datasets/raw/plantseg"))
    parser.add_argument("--target-host", default="tomato")
    parser.add_argument("--target-disease", default="tomato early blight")
    parser.add_argument("--minimum-usable-masks", type=int, default=MINIMUM_USABLE_MASKS)
    args = parser.parse_args()
    if not args.source.is_dir():
        print(f"SETUP REQUIRED: PlantSeg is not available at {args.source}. Place an authorized local copy there or pass --source. This script never downloads data.", file=sys.stderr)
        return 2
    try:
        report = audit_source(args.source, args.target_host, args.target_disease)
    except DatasetSetupError as exc:
        print(f"SETUP REQUIRED: {exc}", file=sys.stderr); return 2
    target = report["target"]
    report["gate"] = {"minimum_usable_masks": args.minimum_usable_masks, "decision": "GO" if target["usable_masks"] >= args.minimum_usable_masks and not report["target_malformed_annotations"] else "NO-GO"}
    print(dump_json(report))
    return 0 if report["gate"]["decision"] == "GO" else 3

if __name__ == "__main__": raise SystemExit(main())
