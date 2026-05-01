#!/usr/bin/env python3
"""Split per-class image folders into train/ and val/ (80/20 by default).

Usage:
    python split_dataset.py raw_photos/ dataset/ --val 0.2

Input layout (what the user has):
    raw_photos/
        healthy/  *.jpg
        sick/     *.jpg

Output layout (what train_classifier.py expects):
    dataset/
        train/healthy/*.jpg   train/sick/*.jpg
        val/healthy/*.jpg     val/sick/*.jpg

Files are COPIED, not moved — the originals stay put.
"""
from __future__ import annotations

import argparse
import random
import shutil
from pathlib import Path

EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("src", help="folder containing one subfolder per class")
    ap.add_argument("dst", help="output folder (will contain train/ and val/)")
    ap.add_argument("--val", type=float, default=0.2, help="fraction for validation")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    src, dst = Path(args.src), Path(args.dst)
    classes = [d for d in sorted(src.iterdir()) if d.is_dir()]
    if not classes:
        raise SystemExit(f"No class subfolders found in {src}")

    rng = random.Random(args.seed)
    total_train = total_val = 0
    for cls in classes:
        imgs = sorted(p for p in cls.iterdir() if p.suffix.lower() in EXTS)
        if not imgs:
            print(f"  (skipping {cls.name}: no images)")
            continue
        rng.shuffle(imgs)
        n_val = max(1, round(len(imgs) * args.val)) if len(imgs) > 1 else 0
        for split, group in [("val", imgs[:n_val]), ("train", imgs[n_val:])]:
            out = dst / split / cls.name
            out.mkdir(parents=True, exist_ok=True)
            for f in group:
                shutil.move(str(f), out / f.name)
        total_train += len(imgs) - n_val
        total_val += n_val
        print(f"  {cls.name:<20} {len(imgs) - n_val:>4} train  {n_val:>4} val")

    print(f"\nDone -> {dst}  (train: {total_train}, val: {total_val})")


if __name__ == "__main__":
    main()
