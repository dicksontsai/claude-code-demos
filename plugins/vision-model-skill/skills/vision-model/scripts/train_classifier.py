#!/usr/bin/env python3
"""Train an image classifier on your own folders. Transfer-learns a small
pretrained network so it works with as few as ~30 images per class.

Usage:
    python train_classifier.py --data dataset/ --out runs/exp1 --epochs 30

Expects:
    dataset/train/<class_a>/*.jpg
    dataset/train/<class_b>/*.jpg
    dataset/val/<class_a>/*.jpg
    dataset/val/<class_b>/*.jpg
(If you only have flat per-class folders, run split_dataset.py first.)

Writes to --out:
    best.pt              the trained model (use with predict.py)
    metrics.csv          one row per epoch: epoch,train_loss,val_loss,val_acc
    predictions.jpg      a grid of validation images with predicted vs true labels
    classes.txt          class names in index order
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import torch
from torch import nn, optim
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms
from torchvision.utils import make_grid


def get_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def build_model(num_classes: int, freeze_backbone: bool) -> nn.Module:
    m = models.mobilenet_v3_small(weights="DEFAULT")
    if freeze_backbone:
        for p in m.features.parameters():
            p.requires_grad = False
    in_feat = m.classifier[-1].in_features
    m.classifier[-1] = nn.Linear(in_feat, num_classes)
    return m


def run_epoch(model, loader, criterion, device, optimizer=None):
    train = optimizer is not None
    model.train(train)
    total_loss, correct, count = 0.0, 0, 0
    with torch.set_grad_enabled(train):
        for x, y in loader:
            x, y = x.to(device), y.to(device)
            out = model(x)
            loss = criterion(out, y)
            if train:
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
            total_loss += loss.item() * x.size(0)
            correct += (out.argmax(1) == y).sum().item()
            count += x.size(0)
    return total_loss / count, correct / count


@torch.inference_mode()
def save_prediction_grid(model, ds, classes, device, out_path: Path, n: int = 16):
    """Save a grid of n val images with 'pred / true' captions baked in."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    n = min(n, len(ds))
    idxs = torch.linspace(0, len(ds) - 1, n).long().tolist()
    imgs, ys = zip(*[ds[i] for i in idxs])
    x = torch.stack(imgs).to(device)
    preds = model(x).argmax(1).cpu().tolist()

    # Un-normalize for display
    mean = torch.tensor([0.485, 0.456, 0.406])[:, None, None]
    std = torch.tensor([0.229, 0.224, 0.225])[:, None, None]
    disp = (torch.stack(imgs) * std + mean).clamp(0, 1)

    cols = 4
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(3 * cols, 3 * rows))
    for ax, img, p, y in zip(axes.flat, disp, preds, ys):
        ax.imshow(img.permute(1, 2, 0))
        ok = "✓" if p == y else "✗"
        color = "green" if p == y else "red"
        ax.set_title(f"{ok} {classes[p]}\n(true: {classes[y]})", fontsize=9, color=color)
        ax.axis("off")
    for ax in list(axes.flat)[n:]:
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", required=True, help="folder with train/ and val/")
    ap.add_argument("--out", default="runs/exp", help="output directory")
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--imgsz", type=int, default=224)
    ap.add_argument("--patience", type=int, default=10, help="stop if val_acc stalls")
    ap.add_argument("--freeze-backbone", action="store_true",
                    help="train only the final layer (use for very small datasets)")
    ap.add_argument("--workers", type=int, default=2)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    device = get_device()
    print(f"device: {device}")

    norm = transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    tf_train = transforms.Compose([
        transforms.RandomResizedCrop(args.imgsz, scale=(0.7, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(0.2, 0.2, 0.2),
        transforms.ToTensor(),
        norm,
    ])
    tf_val = transforms.Compose([
        transforms.Resize(int(args.imgsz * 1.14)),
        transforms.CenterCrop(args.imgsz),
        transforms.ToTensor(),
        norm,
    ])

    data = Path(args.data)
    ds_train = datasets.ImageFolder(data / "train", tf_train)
    ds_val = datasets.ImageFolder(data / "val", tf_train)
    classes = ds_train.classes
    (out / "classes.txt").write_text("\n".join(classes))
    print(f"classes: {classes}")
    print(f"train: {len(ds_train)} images, val: {len(ds_val)} images")

    dl_train = DataLoader(ds_train, batch_size=args.batch, shuffle=True,
                          num_workers=args.workers, pin_memory=(device.type == "cuda"))
    dl_val = DataLoader(ds_val, batch_size=args.batch, shuffle=False,
                        num_workers=args.workers)

    model = build_model(len(classes), args.freeze_backbone).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()),
                            lr=args.lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)

    best_acc, stale = 0.0, 0
    with (out / "metrics.csv").open("w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["epoch", "train_loss", "val_loss", "val_acc"])
        for epoch in range(1, args.epochs + 1):
            tl, ta = run_epoch(model, dl_train, criterion, device, optimizer)
            vl, va = run_epoch(model, dl_val, criterion, device)
            scheduler.step()
            wr.writerow([epoch, f"{tl:.4f}", f"{vl:.4f}", f"{va:.4f}"])
            f.flush()
            tag = ""
            if ta > best_acc:
                best_acc, stale = ta, 0
                torch.save({"model": model.state_dict(), "classes": classes,
                            "arch": "mobilenet_v3_small", "imgsz": args.imgsz},
                           out / "best.pt")
                tag = "  <- best"
            else:
                stale += 1
            print(f"epoch {epoch:3d}/{args.epochs}  train_loss {tl:.3f}  "
                  f"val_loss {vl:.3f}  val_acc {va:.1%}{tag}")
            if stale >= args.patience:
                print(f"(stopping early — no improvement for {args.patience} epochs)")
                break

    # Reload best for the prediction grid
    ckpt = torch.load(out / "best.pt", map_location=device, weights_only=True)
    model.load_state_dict(ckpt["model"])
    save_prediction_grid(model, ds_val, classes, device, out / "predictions.jpg")

    print()
    print(f"Best validation accuracy: {best_acc:.1%}")
    print(f"Saved -> {out}/best.pt, metrics.csv, predictions.jpg, classes.txt")


if __name__ == "__main__":
    main()
