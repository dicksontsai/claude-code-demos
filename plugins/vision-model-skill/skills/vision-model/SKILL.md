---
name: vision-model
description: This skill should be used when the user wants to build, train, or fine-tune a computer-vision model — image classification ("what is this a photo of"), object detection ("find the people / packages / cats in this image"), or visual yes/no checks ("is this product defective"). Trigger on phrases like "train a vision model", "recognize X in images", "detect X in photos", "classify my images", "build an image classifier", "tell what's in front of my camera", "is this picture A or B", or any request that involves teaching a computer to understand photos. The skill assumes the user may be non-technical — produce a working result fast using pretrained models, then iterate.
license: Complete terms in LICENSE
---

# Vision Model Builder

Guide a user — possibly someone who has never trained a model before — from "I want a model that does X with images" to a working model they understand. Prioritize a fast first result over a perfect one, explain every metric in plain English, and always show predictions on real images so the user can judge with their own eyes.

**This skill ships ready-made scripts.** Do not author training loops, datasets, or CLIP code from scratch — copy the templates from this skill's `scripts/` directory into the user's project with the Write tool, then run them. The scripts are already tested; reinventing them risks subtle bugs. Adapt arguments (paths, epochs, class names), not the core logic.

## Communicating with the user

Assume the user is smart but **not** an ML practitioner. Avoid jargon — say "how often it's right" not "top-1 accuracy", "the model is memorizing instead of learning" not "overfitting" (or use the jargon once and define it in five words). Never show a wall of loss curves; show one chart and one number. When the user gives technical signals (mentions PyTorch, GPUs, mAP), match their level.

Ask **at most two** clarifying questions before producing something runnable. The user came here to see a model work, not to fill out a form.

The recipe labels below (A/B/C/D) are internal routing — never surface them. Say "let's train a classifier on your two folders," not "we'll use Recipe A."

**Create runnable files, not just code blocks.** Use the Write tool to put scripts on disk so the user just runs `python <file>.py`; then offer to run it (or, if Bash is unavailable, tell them exactly what to type).

## Step 1 — Triage the task (30 seconds)

Determine two things from the user's request:

**A. Task type**
| User wants | Task | Tell-tale phrasing |
|---|---|---|
| "What is this a photo of?" — one label per image | **Classification** | "is this A or B", "sort my photos", "healthy or sick", "which species" |
| "Where are the X's in this image?" — boxes around things | **Detection** | "find the…", "spot…", "recognize entities", "count how many", "is there a person" |

If genuinely ambiguous, default to **detection** — it answers "what AND where", and a detector can act as a classifier (image contains X if any box has class X).

**B. Data situation** — if the user mentions having images or folders but gives no path, **search for them first with the Glob tool** (patterns like `**/*.jpg`, `**/*.png`, `**/<class-word>/**`, `**/train/**`) before asking. Do not `Read` a directory path — that fails; use Glob or `ls`. Finding their data beats asking where it is.
- **No images yet** → use a pretrained or zero-shot model (no training).
- **Has images but unlabeled** → start pretrained/zero-shot; help label only if needed.
- **Has labeled images** (folders-per-class, or images+boxes) → transfer learning.

Out of scope — say so and redirect: image *generation*, OCR / reading text, medical diagnosis, face *identification* of specific named people.

## Step 2 — Set up the environment

Create a virtual environment and install the open-source stack: **PyTorch + torchvision** (training and pretrained models, BSD license) and **open_clip_torch** (zero-shot classification by text, Apache-2.0). All CPU-capable.

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install torch torchvision open_clip_torch matplotlib pillow
```

Then copy this skill's scripts into the user's project and verify the install:

1. Read the contents of `scripts/check_environment.py` from this skill directory.
2. Write it verbatim to `check_environment.py` in the user's working directory.
3. Run `python check_environment.py`.

If the import check fails on a fresh Python, the usual fix is `pip install --upgrade pip` first (older pip can't resolve torch wheels). If torch refuses to install, point the user to `pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu` for the CPU-only wheel.

**The first run of each model script downloads weights once** (10–75 MB for the training models, ~350 MB for zero-shot CLIP). Mention this so the user isn't surprised by a pause.

## Step 3 — Instant gratification: run something pretrained first

**Always do this before any training**, even if the user has their own data. It proves the pipeline works end-to-end in under a minute and calibrates expectations. Pick whichever fits:

### 3a. Everyday-object detection (91 common classes, no training)

Copy `scripts/predict_pretrained.py` from this skill into the project, then:

```bash
python predict_pretrained.py path/to/user_image.jpg
# or filter to relevant classes:
python predict_pretrained.py front_door.jpg --classes "person,dog,cat,car,bicycle,backpack,suitcase"
```

This draws boxes on the image and saves `<name>_detected.jpg`. The 91 classes cover people, vehicles, animals, furniture, food, electronics — see `references/detection_deep_dive.md` for the list.

### 3b. Zero-shot classification with the user's own words (no training)

When the target isn't in the 91 classes ("raccoon", "blighted leaf", "cracked phone screen"), copy `scripts/zeroshot_classify.py` and run:

```bash
python zeroshot_classify.py porch.jpg --labels "raccoon,cat,dog,empty porch"
```

CLIP picks which of the user's labels best matches each image. Include a "negative" label (e.g. `"empty porch"`) so the model has something to choose when the target is absent.

Show the user the output. **If pretrained or zero-shot is already good enough, stop here** — many "train a model" requests are satisfied without training. Hand off the script and skip to Step 7.

## Step 4 — Train a custom model (only if Step 3 wasn't enough)

Copy the matching script template into the project, then run it. Use the defaults unless the user has a GPU and >1000 images.

### Recipe A — Classification, user has folders per class

The folder *is* the label:
```
dataset/
  train/healthy/*.jpg   train/sick/*.jpg
  val/healthy/*.jpg     val/sick/*.jpg
```
If the user only has flat per-class folders, copy `scripts/split_dataset.py` and run `python split_dataset.py raw/ dataset/` to create the 80/20 split automatically.

Then copy `scripts/train_classifier.py` and run:
```bash
python train_classifier.py --data dataset --out runs/exp1 --epochs 30
```
For very small datasets (<30 images/class) add `--freeze-backbone`.

### Recipe B — Detection, user has images + bounding boxes

Layout (YOLO label format — what free tools like labelImg export):
```
dataset/
  images/train/*.jpg     images/val/*.jpg
  labels/train/*.txt     labels/val/*.txt
  classes.txt
```
Each `.txt` line: `class_id x_center y_center width height` (normalized 0–1). If the user has no boxes yet, point them to `references/data_preparation.md` for free point-and-click labeling tools — never ask them to write coordinate files by hand.

Copy `scripts/train_detector.py` and run:
```bash
python train_detector.py --data dataset --out runs/det1 --epochs 50
```

### Recipe C — Detection, but pretrained classes are *almost* right

Skip training. `predict_pretrained.py --classes "person,dog,car"` filters to just the relevant ones.

### Recipe D — "Is X present, yes or no?" with very few images (<30 per class)

Treat as 2-class classification (Recipe A with `yes/` and `no/` folders, `--freeze-backbone`). Warn the user accuracy will be rough until they reach ~50 per class.

## Step 5 — Show results a human can understand

Every training run writes to `--out` (e.g. `runs/exp1/`): `best.pt`, `metrics.csv`, `predictions.jpg`, `classes.txt`. **Do not** dump raw CSVs or loss curves on a non-technical user. Present three things:

**1. One headline number** — read the last lines the training script printed, or the max of `val_acc`/`val_map50` in `metrics.csv`:
- Classification: *"The model gets it right **87%** of the time on photos it has never seen."*
- Detection: *"When the model draws a box, it's around the right thing about **74%** of the time."*

**2. One simple chart** — copy `scripts/plot_simple_metrics.py` and run `python plot_simple_metrics.py runs/exp1`. It draws a single line (validation accuracy or mAP over training rounds) with the best point marked. Say what to look for: *"The line going up and flattening is good. If it went up then back down, the model started memorizing — that's why we keep the best checkpoint."*

**3. Real predictions** — `runs/exp1/predictions.jpg` is a grid of validation images with ✓/✗ and predicted vs true labels (or boxes). Show it and narrate two or three: *"✓ correctly spotted the package here. ✗ missed this one in shadow — that's the kind of photo to add more of."*

Then run the trained model on a brand-new image with `scripts/predict.py`:
```bash
python predict.py runs/exp1/best.pt new_photo.jpg
```

## Step 6 — Iterate with the user

Read `metrics.csv` and `predictions.jpg`, then ask **one specific, actionable question** — not "how can we improve?" but:

- *"It confuses `sick` with `healthy` when the leaf is in shadow. Can you add ~20 shadowy healthy-leaf photos to `dataset/train/healthy/`?"*
- *"All the misses are small/far-away packages. Want me to retrain with larger input images (`--imgsz 512`, slower), or is close-up good enough?"*
- *"One class has 200 photos, the other has 12 — that's why it always guesses the big class. Can you get more of the small one?"*

To retrain: re-run the same `train_*.py` command with `--out runs/exp2` so results are easy to compare side-by-side. Change one thing at a time. For deeper diagnostics read `references/improving_your_model.md`, and for common failure modes see `references/troubleshooting.md`.

## Step 7 — Hand off something usable

`scripts/predict.py` already works as the standalone inference script — make sure it's in the project root and tell the user:

```bash
python predict.py runs/exp1/best.pt any_new_photo.jpg
```

For a webcam loop, a tiny web demo, or exporting to a phone, read `references/deployment.md`.

---

## Defaults cheat-sheet

| Setting | Classification | Detection | Why |
|---|---|---|---|
| Backbone | `mobilenet_v3_small` | `ssdlite320_mobilenet_v3_large` | Smallest torchvision models; CPU-friendly |
| Weight download | ~10 MB | ~21 MB | One-time |
| Image size | 224 | 320 | Standard for each backbone |
| Epochs | 50 | 100 | Enough for transfer learning on small data |
| Patience (early stop) | 10 | 15 | Stops when val metric plateaus |
| Min images to expect decent results | ~50 / class | ~100 boxes / class | Rule of thumb |

## Scripts in this skill (copy verbatim, then run)

| Script | Purpose |
|---|---|
| `scripts/check_environment.py` | Verify torch/torchvision/open_clip installed; print versions in plain English |
| `scripts/predict_pretrained.py` | 91-class everyday-object detector, zero training, saves annotated image |
| `scripts/zeroshot_classify.py` | CLIP zero-shot: classify against the user's own text labels, zero training |
| `scripts/split_dataset.py` | Turn flat per-class folders into `train/` + `val/` |
| `scripts/train_classifier.py` | Transfer-learn MobileNetV3 on ImageFolder; logs `metrics.csv`, saves `best.pt` + prediction grid |
| `scripts/train_detector.py` | Transfer-learn SSDLite on YOLO-format boxes; same outputs |
| `scripts/predict.py` | Run a trained `best.pt` on new images (auto-detects classify vs detect) |
| `scripts/plot_simple_metrics.py` | One clean accuracy-over-time PNG from `metrics.csv` |

## What's fine-tunable vs. fixed

Be explicit with the user about which paths *learn from their data* and which are frozen pretrained models — it sets the right expectation for "why isn't it picking up my weird thing."

| Path | Trainable on user data? | What it learns |
|---|---|---|
| `train_classifier.py` | **Yes** — full fine-tune (or head-only with `--freeze-backbone`) | Any classes the user defines via folder names. ImageNet-pretrained backbone adapts to the user's photos. |
| `train_detector.py` | **Yes** — full fine-tune | Any box classes the user labels. ImageNet-pretrained backbone + fresh detection head. |
| `predict_pretrained.py` | **No** — frozen COCO weights | Exactly the 91 COCO classes, nothing else. If the target isn't in that list, this script will never find it — switch to fine-tuning or zero-shot. |
| `zeroshot_classify.py` (CLIP) | **No** — frozen CLIP weights | Matches images to *any* text label, but the model itself never updates. Accuracy is whatever CLIP's prior gives; you can't improve it by adding photos. To improve, use its predictions to sort photos into folders and then run `train_classifier.py`. |

Everything trainable here is **transfer learning** — starting from pretrained weights and adapting. There is no from-scratch training (it would fail on the dataset sizes a non-technical user has). Swapping to a larger backbone (ResNet50, EfficientNet, Faster R-CNN) is a one-line edit inside the train scripts — see `references/improving_your_model.md` and `references/detection_deep_dive.md`.

## Reference files (read when needed)

- **`references/data_preparation.md`** — folder layouts, free labeling tools, train/val splitting, "how many images do I need", augmentation.
- **`references/detection_deep_dive.md`** — the 91 pretrained classes, label format details, confidence thresholds.
- **`references/improving_your_model.md`** — plain-English fixes for "accuracy is stuck", overfitting/underfitting, class imbalance, when to use a bigger backbone.
- **`references/deployment.md`** — webcam loop, ONNX/TorchScript export, a 20-line Gradio web demo.
