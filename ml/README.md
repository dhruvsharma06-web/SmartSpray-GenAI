# SmartSpray ML dataset baseline

This directory contains local-only preparation utilities for the V1 target:
**tomato early-blight lesion segmentation**. It does not train a model and does
not contain images, annotations, or model weights.

## Source and attribution

- **Dataset:** PlantSeg: A Large-Scale In-the-wild Dataset for Plant Disease
  Segmentation.
- **Authoritative record:** [Zenodo record](https://doi.org/10.5281/zenodo.17719108),
  PlantSeg v7, archive MD5 `9358a66dff88cdd15c4fe009763c40a3`.
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

The converter discovers the release metadata (`Name`, `Plant`, `Disease`,
`Label file`, and `URL`) and resolves the split image/mask directories from the
release. Non-zero mask regions become class-0 contours, normalized to
Ultralytics polygon coordinates. The verified release uses the exact target
label `tomato early blight`; it contains 153 target images, 150 usable masks,
and 143 unique source URLs. Three target image/mask dimension mismatches leave
the target below the 300-mask gate, so it is not currently suitable as a
standalone training baseline.
This is a lesion-only dataset; the controlled webcam leaf foreground mask
remains a separate stage.

For the local collection protocol, see
[LOCAL_WEBCAM_COLLECTION_PROTOCOL.md](LOCAL_WEBCAM_COLLECTION_PROTOCOL.md).
Validate the manifest before collection review with
`python ml/scripts/validate_local_collection.py ml/datasets/local_webcam/metadata.csv`.
