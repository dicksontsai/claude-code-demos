# Data Preparation

Read this when the user needs to collect, organize, or label images before training.

## How many images are enough?

| Images per class | What to expect |
|---|---|
| <20 | Proof-of-concept only. Model will be shaky. Fine for "is this even possible." |
| 50–100 | Usually enough for a useful classifier on visually distinct classes. |
| 200–500 | Solid. Diminishing returns start here for simple tasks. |
| 1000+ | Only needed for subtle distinctions or many classes. |

For **detection**, count *boxes* not images — 100 boxes of the target across varied backgrounds is a reasonable starting point.

**Variety matters more than quantity.** 50 photos under different lighting / angles / backgrounds beat 500 near-identical frames from one video. Ask: *"Are these all from the same camera at the same time of day? If so, the model will only work in that exact setting."*

## Folder layout — classification

The folder *is* the label. No annotation files needed.

```
dataset/
  train/
    class_a/  img001.jpg ...
    class_b/  ...
  val/
    class_a/  ...
    class_b/  ...
```

If the user hands over flat per-class folders without a split, run `split_dataset.py raw/ dataset/` (copies, doesn't move).

## Folder layout — detection (YOLO label format)

```
dataset/
  images/train/*.jpg     images/val/*.jpg
  labels/train/*.txt     labels/val/*.txt
  classes.txt            (one class name per line)
```

Each line of a `.txt` label file is `class_id x_center y_center width height`, all five numbers, the last four normalized 0–1 relative to image size. An image with no objects gets an **empty** `.txt` file (teaches the model what "nothing here" looks like).

## Labeling tools (free, point-and-click)

Never ask a non-technical user to write `.txt` coordinates by hand. Point them to one of these and have them export in **YOLO format**:

| Tool | Runs | Notes |
|---|---|---|
| **labelImg** | `pip install labelImg` then `labelImg` | Simplest. Desktop app, draw boxes, saves YOLO `.txt` directly. Set format to "YOLO" in the sidebar. |
| **Roboflow** (free tier) | Browser | Drag-drop images, draw boxes, exports a YOLO zip. Easiest for true beginners. |
| **Label Studio** | `pip install label-studio` | Good if also doing classification labels. |

### The label-a-little, train-a-little loop

Don't let the user label 1000 images before seeing any results:

1. Label ~30 images.
2. Train for 30 epochs (~minutes on CPU).
3. Look at `predictions.jpg`. Is it finding *anything* in roughly the right place?
   - **Yes** → label 70 more, retrain. Repeat until happy.
   - **No** → the task may be too hard for this approach, or labels are inconsistent. Debug now, not after 1000 labels.

## Data augmentation

`train_classifier.py` applies flip + crop + color jitter by default; `train_detector.py` applies horizontal flip. Usually leave them alone.

Turn specific ones **off** when they break the task — edit the `tf_train` / `YoloBoxDataset` in the training script:
- Text or arrows that have a "right way up" → remove `RandomHorizontalFlip`
- Color *is* the label (sorting by color) → remove `ColorJitter`

## Common data mistakes

- **Leakage**: the same physical object (or video frames a second apart) in both train and val. Val accuracy looks great; real-world is terrible. Split by *source* (by video, by day, by device), not random shuffle, when images are correlated.
- **One giant class, one tiny class**: model just predicts the big one. Either collect more of the small one, or duplicate its images so counts are within ~3×.
- **Wrong labels**: glance at a few image+txt pairs before training — a misplaced box in `predictions.jpg` after epoch 1 usually means the label file is wrong, not the model.
