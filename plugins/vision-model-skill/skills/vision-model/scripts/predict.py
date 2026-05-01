#!/usr/bin/env python3
"""Run a model trained by train_classifier.py or train_detector.py on new images.

Usage:
    python predict.py runs/exp1/best.pt photo.jpg
    python predict.py runs/exp1/best.pt photos/ --conf 0.5

Auto-detects whether the checkpoint is a classifier or a detector. For
classification prints the top label + confidence. For detection draws boxes
and saves `<image>_pred.jpg`.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import torch
from PIL import Image
from torchvision import models, transforms
from torchvision.models.detection import ssdlite320_mobilenet_v3_large
from torchvision.transforms import functional as TF
from torchvision.utils import draw_bounding_boxes


def load_checkpoint(path: Path, device):
    ckpt = torch.load(path, map_location=device, weights_only=True)
    arch = ckpt["arch"]
    classes = ckpt["classes"]
    if arch == "mobilenet_v3_small":
        m = models.mobilenet_v3_small(weights=None)
        m.classifier[-1] = torch.nn.Linear(m.classifier[-1].in_features, len(classes))
        m.load_state_dict(ckpt["model"])
        task = "classify"
    elif arch == "ssdlite320_mobilenet_v3_large":
        m = ssdlite320_mobilenet_v3_large(weights=None, num_classes=ckpt["num_classes"])
        m.load_state_dict(ckpt["model"])
        task = "detect"
    else:
        raise SystemExit(f"Unknown arch in checkpoint: {arch}")
    m.to(device).eval()
    return m, classes, task, ckpt.get("imgsz", 224)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("checkpoint", help="path to best.pt")
    ap.add_argument("path", help="image file or folder")
    ap.add_argument("--conf", type=float, default=0.4, help="(detection) min confidence")
    args = ap.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model, classes, task, imgsz = load_checkpoint(Path(args.checkpoint), device)
    print(f"loaded {task} model — classes: {classes}")

    src = Path(args.path)
    images = (
        sorted(p for p in src.iterdir()
               if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"})
        if src.is_dir() else [src]
    )

    if task == "classify":
        tf = transforms.Compose([
            transforms.Resize(int(imgsz * 1.14)),
            transforms.CenterCrop(imgsz),
            transforms.ToTensor(),
            transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5]),
        ])
        for p in images:
            x = tf(Image.open(p).convert("RGB")).unsqueeze(0).to(device)
            with torch.inference_mode():
                prob = model(x).softmax(1)[0]
            i = prob.argmax().item()
            print(f"{p.name:<30} -> {classes[i]:<20} ({prob[i]:.0%})")
    else:
        for p in images:
            img = Image.open(p).convert("RGB").resize((imgsz, imgsz))
            x = TF.to_tensor(img).to(device)
            with torch.inference_mode():
                out = model([x])[0]
            keep = out["scores"] <= args.conf
            boxes = out["boxes"][keep].cpu()
            names = [f"{classes[l - 1]} {s:.0%}"
                     for l, s in zip(out["labels"][keep].tolist(),
                                     out["scores"][keep].tolist())]
            disp = (TF.to_tensor(img) * 255).byte()
            drawn = draw_bounding_boxes(disp, boxes, names, colors="lime", width=3)
            out_p = p.with_name(p.stem + "_pred.jpg")
            Image.fromarray(drawn.permute(1, 2, 0).numpy()).save(out_p)
            shown = ", ".join(names[:10]) + (f", … (+{len(names)-10} more)" if len(names) > 10 else "")
            print(f"{p.name:<30} -> {len(boxes)} object(s): "
                  f"{shown or '(none above threshold)'}")
            print(f"  saved -> {out_p}")


if __name__ == "__main__":
    main()
