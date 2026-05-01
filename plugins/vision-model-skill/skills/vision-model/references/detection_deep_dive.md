# Detection Deep Dive

Read this when working on an object-detection task and the SKILL.md recipe needs more detail.

## The pretrained 91 classes (COCO)

`predict_pretrained.py` uses a small Faster R-CNN trained on COCO. It already detects: person, bicycle, car, motorcycle, airplane, bus, train, truck, boat, traffic light, fire hydrant, stop sign, parking meter, bench, bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe, backpack, umbrella, handbag, tie, suitcase, frisbee, skis, snowboard, sports ball, kite, baseball bat, baseball glove, skateboard, surfboard, tennis racket, bottle, wine glass, cup, fork, knife, spoon, bowl, banana, apple, sandwich, orange, broccoli, carrot, hot dog, pizza, donut, cake, chair, couch, potted plant, bed, dining table, toilet, tv, laptop, mouse, remote, keyboard, cell phone, microwave, oven, toaster, sink, refrigerator, book, clock, vase, scissors, teddy bear, hair drier, toothbrush.

If the user's target maps onto these (e.g. "delivery package" ≈ backpack/suitcase/handbag, "vehicle" ≈ car/truck/bus/motorcycle), filter rather than train:

```bash
python predict_pretrained.py img.jpg --classes "backpack,handbag,suitcase" --conf 0.3
```

## When the target isn't in the 91 classes

There is no open-vocabulary *detector* in this stack (that requires a much larger model). Two options:

1. **Zero-shot *classification*** with `zeroshot_classify.py` answers "does this image contain a raccoon" but not "where is the raccoon". Often that's enough — e.g. for an alert.
2. **Label ~100 boxes and fine-tune** with `train_detector.py`. Use the label-a-little-train-a-little loop in `data_preparation.md`.

## Confidence threshold

`--conf` (default 0.5 for pretrained, 0.4 for custom): lower → more boxes, more false positives. Raise to 0.6+ for "only tell me when you're sure"; drop to 0.2 for "show me everything plausible".

## Explaining mAP to a non-technical user

`val_map50` is the headline detection metric in `metrics.csv`. Translate it as:

> *"Across all the test photos, when the model draws a box, about **{map50×100:.0f}%** of the time it's around the right thing in roughly the right place. 60%+ is useful, 80%+ is very good for a small custom dataset."*

(Our `train_detector.py` computes a simplified F1@IoU0.5 — close enough to mAP50 for small-dataset comparisons, and far easier to explain than the full PR-curve integral.)

## When to move past the small backbone

Stick with SSDLite-MobileNetV3 unless **all** of: dataset >1000 boxes, GPU available, and `val_map50` plateaued below target. Then in `train_detector.py` swap the model line for:

```python
from torchvision.models.detection import fasterrcnn_resnet50_fpn_v2
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
model = fasterrcnn_resnet50_fpn_v2(weights="DEFAULT")
in_feat = model.roi_heads.box_predictor.cls_score.in_features
model.roi_heads.box_predictor = FastRCNNPredictor(in_feat, num_classes)
```

~5× slower; usually +5–10 points mAP.

## Reading detection results in code

`predict.py` already prints a summary. To process results programmatically:

```python
out = model([img_tensor])[0]
for box, label, score in zip(out["boxes"], out["labels"], out["scores"]):
    if score < 0.4:
        continue
    x1, y1, x2, y2 = box.tolist()
    name = classes[label - 1]  # label 0 is background
```
