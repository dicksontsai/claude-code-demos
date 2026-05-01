#!/usr/bin/env python3
"""Zero-shot image classification with CLIP — no training, your own labels.

Usage:
    python zeroshot_classify.py image.jpg --labels "raccoon,cat,dog,empty porch"
    python zeroshot_classify.py photos/ --labels "healthy leaf,blighted leaf"

Tells you which of YOUR labels best matches each image, using a model that
was trained to connect pictures and words. Great when you have no labeled
data yet and want to see if the categories are even visually distinguishable.

First run downloads ~350 MB of weights (one time).
"""
from __future__ import annotations

import argparse
from pathlib import Path

import warnings

import open_clip
import torch
from PIL import Image

# Cosmetic: openai ViT-B-32 weights trigger a harmless QuickGELU mismatch warning.
warnings.filterwarnings("ignore", message=".*QuickGELU mismatch.*")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path", help="image file or folder of images")
    ap.add_argument(
        "--labels",
        required=True,
        help='comma-separated labels in your own words, e.g. "raccoon,cat,empty porch"',
    )
    ap.add_argument("--model", default="ViT-B-32")
    ap.add_argument("--pretrained", default="openai")
    args = ap.parse_args()

    labels = [s.strip() for s in args.labels.split(",") if s.strip()]
    if len(labels) < 2:
        raise SystemExit("Give at least two labels so the model has something to choose between.")

    device = (
        "cuda" if torch.cuda.is_available()
        else "mps" if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available()
        else "cpu"
    )
    model, _, preprocess = open_clip.create_model_and_transforms(
        args.model, pretrained=args.pretrained, device=device
    )
    model.eval()
    tokenizer = open_clip.get_tokenizer(args.model)

    prompts = [f"a photo of {t}" for t in labels]
    with torch.inference_mode():
        text_feat = model.encode_text(tokenizer(prompts).to(device))
        text_feat /= text_feat.norm(dim=-1, keepdim=True)

    src = Path(args.path)
    images = (
        sorted(p for p in src.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"})
        if src.is_dir() else [src]
    )
    if not images:
        raise SystemExit(f"No images found at {src}")

    print(f"{'image':<30} {'best guess':<24} conf   (runner-up)")
    print("-" * 78)
    for p in images:
        img = preprocess(Image.open(p).convert("RGB")).unsqueeze(0).to(device)
        with torch.inference_mode():
            img_feat = model.encode_image(img)
            probs = (100 * img_feat @ text_feat.T).softmax(dim=-1)[0]
        top2 = probs.topk(min(2, len(labels)))
        best_i = top2.indices[0].item()
        line = f"{p.name:<30} {labels[best_i]:<24} {probs[best_i]:.0%}"
        if len(labels) > 1:
            ru = top2.indices[1].item()
            line += f"   ({labels[ru]} {probs[ru]:.0%})"
        print(line)

    print()
    print("These are the model's best guesses among ONLY the labels you gave.")
    print("If accuracy looks promising, you can use this to sort photos into folders")
    print("and then train a dedicated classifier (train_classifier.py) for higher accuracy.")


if __name__ == "__main__":
    main()
