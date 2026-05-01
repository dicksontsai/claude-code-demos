#!/usr/bin/env python3
"""Train an object detector on your own boxes. Transfer-learns a small
SSDLite network so it works with ~100 labeled boxes per class on a CPU.

Usage:
    python train_detector.py --data dataset/ --out runs/det1 --epochs 50

Expects YOLO-format labels (what labelImg / Roboflow export):
    dataset/
        images/train/*.jpg     images/val/*.jpg
        labels/train/*.txt     labels/val/*.txt   (one .txt per image)
        classes.txt            (one class name per line, index order)

Each .txt line: `class_id x_center y_center width height` (all 0-1).

Writes to --out:
    best.pt              the trained model (use with predict.py --task detect)
    metrics.csv          epoch,train_loss,val_loss,val_map50
    predictions.jpg      grid of val images with predicted boxes drawn
    classes.txt
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms as T
from torchvision.models.detection import ssdlite320_mobilenet_v3_large
from torchvision.ops import box_iou
from torchvision.transforms import functional as TF
from torchvision.utils import draw_bounding_boxes


# ----------------------------------------------------------------------
# Dataset: reads images + YOLO-format txt labels
# ----------------------------------------------------------------------
class YoloBoxDataset(Dataset):
    def __init__(self, root: Path, split: str, imgsz: int, train: bool):
        self.imgsz = imgsz
        self.train = train
        self.img_dir = root / "images" / split
        self.lbl_dir = root / "labels" / split
        self.paths = sorted(
            p for p in self.img_dir.iterdir()
            if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
        )
        if not self.paths:
            raise SystemExit(f"No images in {self.img_dir}")

    def __len__(self):
        return len(self.paths)

    def __getitem__(self, i):
        p = self.paths[i]
        img = Image.open(p).convert("RGB")
        w0, h0 = img.size
        boxes, labels = [], []
        lbl = self.lbl_dir / (p.stem + ".txt")
        if lbl.exists():
            for line in lbl.read_text().splitlines():
                parts = line.split()
                if len(parts) != 5:
                    continue
                c, xc, yc, bw, bh = parts
                xc, yc, bw, bh = float(xc) * w0, float(yc) * h0, float(bw) * w0, float(bh) * h0
                boxes.append([xc - bw / 2, yc - bh / 2, xc + bw / 2, yc + bh / 2])
                labels.append(int(c) + 1)  # 0 reserved for background
        # Resize image and boxes to square imgsz
        img = img.resize((self.imgsz, self.imgsz))
        sx, sy = self.imgsz / w0, self.imgsz / h0
        boxes = torch.tensor(boxes, dtype=torch.float32).reshape(-1, 4)
        if len(boxes):
            boxes[:, [0, 2]] *= sx
            boxes[:, [1, 3]] *= sy
        labels = torch.tensor(labels, dtype=torch.int64)
        # Horizontal flip augmentation (training only)
        if self.train and torch.rand(1) < 0.5:
            img = TF.hflip(img)
            if len(boxes):
                boxes[:, [0, 2]] = self.imgsz - boxes[:, [2, 0]]
        return TF.to_tensor(img), {"boxes": boxes, "labels": labels}


def collate(batch):
    return tuple(zip(*batch))


# ----------------------------------------------------------------------
# Simple mAP@0.5 (per-image greedy match) — good enough for small datasets
# ----------------------------------------------------------------------
@torch.inference_mode()
def evaluate(model, loader, device, conf=0.3):
    model.eval()
    tp, n_pred, n_gt = 0, 0, 0
    losses = []
    for imgs, targets in loader:
        imgs = [i.to(device) for i in imgs]
        tgt = [{k: v.to(device) for k, v in t.items()} for t in targets]
        # val loss (model needs train mode to return loss dict)
        model.train()
        with torch.no_grad():
            ld = model(imgs, tgt)
            losses.append(sum(ld.values()).item())
        model.eval()
        outs = model(imgs)
        for out, t in zip(outs, targets):
            keep = out["scores"] >= conf
            pb, pl = out["boxes"][keep].cpu(), out["labels"][keep].cpu()
            gb, gl = t["boxes"], t["labels"]
            n_pred += len(pb)
            n_gt += len(gb)
            if len(pb) == 0 or len(gb) == 0:
                continue
            iou = box_iou(pb, gb)
            matched = set()
            for pi in iou.max(dim=1).values.argsort(descending=True):
                gi = iou[pi].argmax().item()
                if iou[pi, gi] >= 0.5 and gi not in matched and pl[pi] == gl[gi]:
                    matched.add(gi)
                    tp += 1
    prec = tp / max(n_pred, 1)
    rec = tp / max(n_gt, 1)
    map50 = (2 * prec * rec / max(prec + rec, 1e-9))  # F1 proxy for "useful detection rate"
    return sum(losses) / max(len(losses), 1), map50


@torch.inference_mode()
def save_prediction_grid(model, ds, classes, device, out_path, n=6, conf=0.3):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    model.eval()
    n = min(n, len(ds))
    fig, axes = plt.subplots(2, 3, figsize=(12, 8))
    for ax, i in zip(axes.flat, range(n)):
        img, _ = ds[i]
        out = model([img.to(device)])[0]
        keep = out["scores"] >= conf
        boxes = out["boxes"][keep].cpu()
        names = [f"{classes[l - 1]} {s:.0%}"
                 for l, s in zip(out["labels"][keep].tolist(), out["scores"][keep].tolist())]
        disp = (img * 255).byte()
        drawn = draw_bounding_boxes(disp, boxes, names, colors="lime", width=3)
        ax.imshow(drawn.permute(1, 2, 0))
        ax.axis("off")
    for ax in list(axes.flat)[n:]:
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def get_device():
    if torch.cuda.is_available():
        return torch.device("cuda")
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", default="runs/det")
    ap.add_argument("--epochs", type=int, default=50)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--lr", type=float, default=5e-4)
    ap.add_argument("--imgsz", type=int, default=320)
    ap.add_argument("--patience", type=int, default=15)
    ap.add_argument("--workers", type=int, default=2)
    args = ap.parse_args()

    data = Path(args.data)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    classes = (data / "classes.txt").read_text().split()
    (out / "classes.txt").write_text("\n".join(classes))
    num_classes = len(classes) + 1  # + background
    device = get_device()
    print(f"device: {device}  classes: {classes}")

    ds_train = YoloBoxDataset(data, "train", args.imgsz, train=True)
    ds_val = YoloBoxDataset(data, "val", args.imgsz, train=False)
    dl_train = DataLoader(ds_train, args.batch, shuffle=True,
                          collate_fn=collate, num_workers=args.workers)
    dl_val = DataLoader(ds_val, args.batch, shuffle=False,
                        collate_fn=collate, num_workers=args.workers)
    print(f"train: {len(ds_train)} images, val: {len(ds_val)} images")

    model = ssdlite320_mobilenet_v3_large(
        weights=None, weights_backbone="DEFAULT", num_classes=num_classes
    ).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)

    best, stale = 0.0, 0
    with (out / "metrics.csv").open("w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(["epoch", "train_loss", "val_loss", "val_map50"])
        for epoch in range(1, args.epochs + 1):
            model.train()
            tl, nb = 0.0, 0
            for imgs, targets in dl_train:
                imgs = [i.to(device) for i in imgs]
                tgt = [{k: v.to(device) for k, v in t.items()} for t in targets]
                loss = sum(model(imgs, tgt).values())
                loss.backward()
                optimizer.step()
                tl += loss.item()
                nb += 1
            scheduler.step()
            tl /= max(nb, 1)
            vl, vm = evaluate(model, dl_val, device)
            wr.writerow([epoch, f"{tl:.4f}", f"{vl:.4f}", f"{vm:.4f}"])
            f.flush()
            tag = ""
            if vm > best:
                best, stale = vm, 0
                torch.save({"model": model.state_dict(), "classes": classes,
                            "arch": "ssdlite320_mobilenet_v3_large",
                            "imgsz": args.imgsz, "num_classes": num_classes},
                           out / "best.pt")
                tag = "  <- best"
            else:
                stale += 1
            print(f"epoch {epoch:3d}/{args.epochs}  train_loss {tl:.3f}  "
                  f"val_loss {vl:.3f}  val_map50 {vm:.1%}{tag}")
            if stale >= args.patience:
                print(f"(stopping early — no improvement for {args.patience} epochs)")
                break

    ckpt = torch.load(out / "best.pt", map_location=device, weights_only=True)
    model.load_state_dict(ckpt["model"])
    save_prediction_grid(model, ds_val, classes, device, out / "predictions.jpg")
    print()
    print(f"Best val mAP50: {best:.1%}")
    print(f"Saved -> {out}/best.pt, metrics.csv, predictions.jpg, classes.txt")


if __name__ == "__main__":
    main()
