# Improving Your Model

Read this when the first training run is done and the user wants better results. Diagnose first, then apply one fix at a time.

## Read the symptoms

Open `runs/.../metrics.csv` (or the simple plot) and `predictions.jpg`.

| Symptom | Plain-English meaning | Likely fix |
|---|---|---|
| `train_loss` low, `val_acc` much lower than train accuracy | **Memorizing** ("overfitting") — learned your exact photos, not the concept | More varied data; or `--freeze-backbone`; or fewer `--epochs` |
| Both train *and* val poor | **Under-powered** — task hard or data too little/noisy | More data; check labels; more `--epochs`; bigger backbone |
| `val_acc` still climbing when training stopped | Stopped too soon | More `--epochs`, higher `--patience` |
| `val_acc` climbed then dropped | Memorizing kicked in mid-run | Fine — `best.pt` already saved the peak. Nothing to do. |
| One class always predicted, others ignored | **Imbalance** — that class has way more examples | Balance counts within ~3× (collect more, or duplicate the small class) |
| `predictions.jpg` shows two specific classes swapped a lot | Those two look alike to the model | Add images that highlight the difference; or merge them if the user doesn't actually need them separate |
| Detection: misses small/far objects | Input resolution too low | `--imgsz 512` (slower) |
| Works on val set, fails on user's real new photos | Val set isn't representative | Rebuild val from truly held-out sources; add real-condition photos to train |

## The single most effective fix

**Add more of whatever it gets wrong.** Look at `predictions.jpg`, find the ✗ cases, and ask the user for 20–30 more photos *like those*. This beats every flag tweak for small datasets.

Concretely:
```bash
python predict.py runs/exp1/best.pt folder_of_new_images/
# Review the printed labels with the user, sort into "got it" / "missed it",
# add the misses (correctly labeled) to dataset/train/<class>/.
python train_classifier.py --data dataset --out runs/exp2 --epochs 30
```

## Knobs worth turning (one at a time)

Only after the data is as good as it'll get:

| Knob | Try when | How |
|---|---|---|
| Bigger backbone | Plateaued, have GPU | In `train_classifier.py`: swap `mobilenet_v3_small` → `efficientnet_b0` or `resnet50`. In `train_detector.py`: see detection_deep_dive.md |
| More epochs | Curve still rising at the end | `--epochs 100 --patience 30` |
| Larger images | Missing fine details | `--imgsz 320` (cls) / `--imgsz 512` (det) |
| Freeze backbone | Very little data (<30/class) | `--freeze-backbone` (cls) — trains only the final layer |
| Lower learning rate | `train_loss` jumps around wildly | `--lr 0.0003` |
| Disable augments | Orientation/color *is* the label | Edit `tf_train` in `train_classifier.py` — remove `RandomHorizontalFlip()` or `ColorJitter` |

Change **one** thing, retrain to a new `--out`, compare the headline number side by side.

## When to stop

Ask the user what "good enough" means *in their world*. "Alert me if there *might* be a package" tolerates false positives; "automatically unlock the door" does not. Tune `--conf` accordingly and stop when the *use case* is satisfied — not when a metric hits an arbitrary number.
