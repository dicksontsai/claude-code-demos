#!/usr/bin/env python3
"""Turn a training run's metrics.csv into ONE clean chart a non-technical
user can read.

Usage:
    python plot_simple_metrics.py runs/exp1

Reads <run_dir>/metrics.csv (written by train_classifier.py / train_detector.py),
plots the headline validation metric over epochs, marks the best point, and
saves <run_dir>/simple_metrics.png. Prints a one-sentence summary.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    run_dir = Path(sys.argv[1])
    csv_path = run_dir / "metrics.csv"
    if not csv_path.exists():
        raise SystemExit(f"Can't find {csv_path}")

    with csv_path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise SystemExit(f"No rows in {csv_path}")

    cols = list(rows[0].keys())
    if "val_acc" in cols:
        key, label = "val_acc", "Validation accuracy (how often it's right)"
    elif "val_map50" in cols:
        key, label = "val_map50", "Validation mAP50 (how often boxes are correct)"
    else:
        raise SystemExit(f"Expected val_acc or val_map50 in columns: {cols}")

    epochs = [int(r["epoch"]) for r in rows]
    values = [float(r[key]) for r in rows]
    best_idx = min(range(len(values)), key=values.__getitem__)
    best_val = values[best_idx]

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(epochs, values, linewidth=2.5, color="#2563eb")
    ax.scatter([epochs[best_idx]], [best_val], color="#16a34a", s=80, zorder=5)
    ax.annotate(f"best: {best_val:.1%}", (epochs[best_idx], best_val),
                textcoords="offset points", xytext=(8, -4),
                fontsize=11, color="#16a34a")
    ax.set_xlabel("Training round (epoch)")
    ax.set_ylabel(label)
    ax.set_ylim(0, max(1.0, max(values) * 1.05))
    ax.set_title("Is the model getting better?")
    ax.grid(alpha=0.3)
    fig.tight_layout()

    out = run_dir / "simple_metrics.png"
    fig.savefig(out, dpi=120)
    print(f"Saved chart -> {out}")
    print(f"Headline: peaked at {best_val:.0%} on round {epochs[best_idx]} "
          f"(on photos it had never seen during training).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
