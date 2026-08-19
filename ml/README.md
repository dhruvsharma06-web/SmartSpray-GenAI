# SmartSpray ML dataset baseline

This directory contains local-only preparation utilities for the V1 target:
**tomato early-blight lesion segmentation**. It does not train a model and does
not contain images, annotations, or model weights.

## Source and attribution

- **Dataset:** PlantSeg: A Large-Scale In-the-wild Dataset for Plant Disease
  Segmentation.
- **Authoritative record:** [Zenodo record](https://doi.org/10.5281/zenodo.17719108)
  and the [data descriptor](https://doi.org/10.1038/s41597-025-06513-4).
- **License:** Creative Commons Attribution-NonCommercial 4.0 International
  (CC BY-NC 4.0), as stated by the current PlantSeg data descriptor. Preserve
  attribution and re-check per-image metadata/licensing before use.
- **Citation:** Wei, T. et al., “A Large-Scale In-the-wild Dataset for Plant
  Disease Segmentation,” *Scientific Data* 13, 205 (2026).

Do not redistribute source images or masks from this repository. The scripts
only transform an authorized local copy into local Ultralytics labels.

## Workflow

1. Obtain PlantSeg under its license and place it at
   `ml/datasets/raw/plantseg/` (or pass `--source`). Do not commit it.
2. Run `python ml/scripts/audit_plantseg.py`. It emits deterministic JSON and
   returns `GO` only at 300 usable target masks with no malformed target masks.
3. Only after GO, run `python ml/scripts/prepare_plantseg.py`.
4. Run `python ml/scripts/validate_dataset.py` before later training work.

The converter discovers the release metadata and requires metadata mappings
from images to grayscale disease masks. Non-zero mask regions become class-0
contours, normalized to Ultralytics polygon coordinates. This is a lesion-only
dataset; the controlled webcam leaf foreground mask remains a separate stage.
