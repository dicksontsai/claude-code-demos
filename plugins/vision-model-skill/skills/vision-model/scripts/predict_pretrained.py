#!/usr/bin/env python3
"""Instant gratification: detect everyday objects in one image, zero training.

Usage:
    python predict_pretrained.py path/to/image.jpg
    python predict_pretrained.py path/to/image.jpg --classes person,dog,car

Uses a small COCO-pretrained detector (91 everyday classes: person, car, dog,
cat, chair, laptop, bottle, ...). Draws boxes on the image and saves
`<image>_detected.jpg` next to the original.

First run downloads ~74 MB of weights.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import torch
from PIL import Image
from torchvision.io import decode_image
from torchvision.models.detection import (
    FasterRCNN_MobileNet_V3_Large_320_FPN_Weights as Weights,
    fasterrcnn_mobilenet_v3_large_320_fpn,
)
from torchvision.utils import draw_bounding_boxes


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("image", help="path to a .jpg/.png image")
    ap.add_argument("--conf", type=float, default=0.5, help="min confidence (0-1)")
    ap.add_argument(
        "--classes",
        default="",
        help="comma-separated class names to keep (default: all 91)",
    )
    args = ap.parse_args()

    weights = Weights.DEFAULT
    categories = weights.meta["categories"]
    keep = set(c.strip() for c in args.classes.split(",") if c.strip()) or None
    if keep:
        unknown = keep - set(categories)
        if unknown:
            print(f"(ignoring unknown class names: {sorted(unknown)})")

    model = fasterrcnn_mobilenet_v3_large_320_fpn(weights=weights)
    model.eval()
    preprocess = weights.transforms()

    img = decode_image(args.image)  # uint8 [C,H,W]
    with torch.inference_mode():
        out = model([preprocess(img)])[0]

    boxes, labels, scores = out["boxes"], out["labels"], out["scores"]
    mask = scores >= args.conf
    if keep:
        mask &= torch.tensor([categories[i - 1] in keep for i in labels])
    boxes, labels, scores = boxes[mask], labels[mask], scores[mask]

    names = [f"{categories[i - 1]} {s:.0%}" for i, s in zip(labels.tolist(), scores.tolist())]
    drawn = draw_bounding_boxes(img, boxes, names, colors="lime", width=3)

    out_path = Path(args.image).with_name(Path(args.image).stem + "_detected.jpg")
    Image.fromarray(drawn.permute(1, 2, 0).numpy()).save(out_path)

    if names:
        print("Found:")
        for n in names:
            print(f"  - {n}")
    else:
        print("Nothing detected above the confidence threshold.")
        print("Try lowering --conf, or this image may not contain any of the 91 everyday classes.")
    print(f"\nAnnotated image saved -> {out_path}")


if __name__ == "__main__":
    main()
