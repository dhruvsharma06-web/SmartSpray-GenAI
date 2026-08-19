# Local dataset protocol

`raw/`, `processed/`, and generated manifest files are ignored by Git. Keep an
authorized PlantSeg copy under `raw/plantseg/`; generated YOLO data is written
under `processed/plantseg_tomato_early_blight/` and its deterministic paths are
recorded in `manifests/`.

The verified local source is PlantSeg v7 from Zenodo record 17719108. Its
metadata uses `Name`, `Plant`, `Disease`, `Label file`, `URL`, and `Split`; the
target disease label is `tomato early blight`. The release is CC BY-NC 4.0 and
must not be redistributed through this repository. The verified target subset
contains 153 images, 150 usable masks, and 3 image/mask dimension mismatches.

## Controlled webcam collection

Collect approximately 100–200 locally captured samples with one tomato leaf on
a fixed matte dark or blue backing board. Record leaf/session identity so all
frames from one leaf/session stay in one split. Vary distance, angle, lighting,
lesion size, backing-board position, exposure, healthy-looking leaves, and
partial occlusion. Capture the same conditions expected in the demo.

- **Training:** may support future fine-tuning; do not include final evaluation
  leaves/sessions.
- **Validation:** used for model and threshold selection; keep sessions and
  leaves disjoint from training.
- **Final webcam evaluation:** held out before training and never used for
  threshold/model selection. It is the only set used to report live-demo
  readiness.

The backing board is intentional: it allows a reliable leaf foreground mask,
which is the denominator for later severity measurement. “Healthy-looking”
means no target early-blight lesion is visible; it is not a general plant-health
diagnosis.
