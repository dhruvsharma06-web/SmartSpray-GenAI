# AI-003 Local Webcam Collection Protocol

This protocol collects approximately 100-200 distinct tomato-leaf samples for early-blight lesion segmentation. It creates data only; it does not train a model, calculate severity, or control hardware.

## Identity Rules

- `plant_id` identifies the physical tomato plant, for example `PLANT-001`.
- `leaf_id` identifies one physical leaf and must remain stable for every capture of that leaf, for example `PLANT-001-LEAF-003`.
- `session_id` identifies one collection session on one day/setup, for example `2026-08-19-S01`.
- `capture_id` identifies one image and must be globally unique, for example `PLANT-001-LEAF-003-S01-C004`.
- Multiple captures of one leaf are allowed, but all captures of a leaf and session must stay in one split.
- Evaluation leaves and sessions must be selected before training and never reused in train, validation, or threshold tuning.

Target approximately 100-200 distinct leaves, not merely 100-200 frames. Use multiple plants where available. A practical allocation is 70% train, 15% validation, and 15% final evaluation by leaf, with no identity overlap. The validator also prevents a plant from appearing in the evaluation split when that plant has non-evaluation rows.

## Controlled Setup

- Fixed laptop webcam on a stable mount; record camera index and resolution in the session log.
- One tomato leaf per frame, mounted or held against a matte dark blue/black backing board.
- Keep the leaf fully visible when possible; record partial occlusion explicitly.
- Avoid glare, motion blur, clipped highlights, severe shadows, and backgrounds that resemble lesions.
- Do not activate the pump or any ESP32 command during collection.

For each selected leaf, capture a short sequence covering:

- Distance: near, nominal demo distance, and far within the camera's usable focus range.
- Angle: front-on plus modest left/right and up/down rotations.
- Lighting: diffuse indoor light, mild side light, and controlled lower-light conditions without blur.
- Leaf position: centered and shifted within the frame.
- Lesion visibility: small, medium, and larger visible lesion coverage when present.
- Healthy-looking leaves: include clean-looking examples, but label them only as `healthy_looking`, not disease-free or generally healthy.

Do not oversample a single leaf to satisfy the count. A leaf's sequence should usually be 3-8 captures, with fewer captures when they are visually redundant.

## Directory Layout

All image and annotation content remains ignored and local:

```text
ml/datasets/local_webcam/
  images/
    train/
    val/
    evaluation/
  labels/
    train/
    val/
    evaluation/
  metadata.csv
  sessions.csv
  README.local.md
```

`test` may be used as a development holdout, but `evaluation` is the final webcam evaluation set and must remain untouched until the end. Do not commit any files beneath `local_webcam/` except an optional local-only README if needed.

## File Naming

Image filenames use:

```text
{plant_id}_{leaf_id}_{session_id}_{capture_id}.jpg
```

Use lowercase ASCII identifiers with hyphens or underscores only. The filename and `capture_id` must agree. Store the corresponding label at the same relative location under `labels/` with a `.txt` extension.

## Metadata Format

`metadata.csv` must contain these columns:

```text
capture_id,plant_id,leaf_id,session_id,split,image_path,annotation_path,label_state,distance_cm,angle_deg,lighting,occlusion,notes
```

Allowed `split` values: `train`, `val`, `test`, `evaluation`.

Allowed `label_state` values:

- `healthy_looking`: no visible target early-blight lesion; annotation file exists and is empty.
- `lesion_present`: one or more visible target lesions; annotation file contains class-0 polygons.
- `uncertain`: visibility or disease identity is not adequate; exclude from training and validation, and review before evaluation.

`lighting` should use controlled values such as `diffuse`, `side_mild`, or `low_controlled`. `occlusion` should be `none`, `partial_leaf`, or `minor_handling`.

Example:

```csv
capture_id,plant_id,leaf_id,session_id,split,image_path,annotation_path,label_state,distance_cm,angle_deg,lighting,occlusion,notes
plant-001_leaf-003_20260819-s01_c001,plant-001,plant-001-leaf-003,20260819-s01,train,images/train/plant-001_leaf-003_20260819-s01_c001.jpg,labels/train/plant-001_leaf-003_20260819-s01_c001.txt,lesion_present,42,0,diffuse,none,
plant-004_leaf-002_20260820-s02_c001,plant-004,plant-004-leaf-002,20260820-s02,train,images/train/plant-004_leaf-002_20260820-s02_c001.jpg,labels/train/plant-004_leaf-002_20260820-s02_c001.txt,healthy_looking,38,5,side_mild,none,no_visible_target_lesion
```

## Annotation Format

Use Ultralytics segmentation label text. One visible lesion instance per line:

```text
0 x1 y1 x2 y2 x3 y3 ...
```

- Class `0` is `early_blight_lesion`.
- Coordinates are normalized to `[0, 1]` in image-relative `x,y` order.
- At least three points are required per polygon.
- Trace only visible lesion pixels, not the entire leaf.
- Separate disconnected lesions into separate polygons.
- Do not infer hidden lesion area.
- Healthy-looking labels must be valid empty `.txt` files.
- Uncertain samples are not training labels; keep them in a review folder or mark them for exclusion.

Annotate with the image at its original resolution. A second reviewer should inspect every lesion-present mask. Reject or revise masks with missing visible lesions, polygons outside image boundaries, self-intersections, excessive background, or ambiguous disease evidence.

## Quality Control

Reject captures with blur, focus failure, severe glare, clipped exposure, duplicated frames, unlabeled identity, or an unresolvable leaf/session. Reject masks that are empty for `lesion_present`, non-empty for `healthy_looking`, dimension-mismatched, outside `[0,1]`, or drawn around non-lesion artifacts.

Before splitting, run:

```powershell
python ml/scripts/validate_local_collection.py ml/datasets/local_webcam/metadata.csv
```

The command must report `valid: true`. It rejects duplicate capture IDs and any plant/leaf/session appearing in multiple splits. Then use the existing dataset validation/conversion tools only after the collection has passed review.

## Evaluation Isolation

Create the `evaluation` leaf/session list first and record it in `sessions.csv`. Do not use evaluation images to select confidence thresholds, edit annotation rules, tune preprocessing, or choose a model. Evaluation images are only for the final webcam-readiness report. Keep a separate backup of the evaluation manifest outside training workspaces.
