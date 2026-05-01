#!/usr/bin/env python3
"""Friendly environment check for the vision-model skill.

Verifies torch / torchvision / open_clip / matplotlib import cleanly and
prints versions in plain English. Does NOT download model weights.

Exit 0 if ready, 1 otherwise.
"""
from __future__ import annotations

import sys


def _ok(msg: str) -> None:
    print(f"  [ok]    {msg}")


def _note(msg: str) -> None:
    print(f"  [note]  {msg}")


def _fail(msg: str) -> None:
    print(f"  [FAIL]  {msg}")


def main() -> int:
    print("Vision-model environment check")
    print("-" * 40)

    py = sys.version_info
    if py >= (3, 9):
        _ok(f"Python {py.major}.{py.minor}.{py.micro}")
    else:
        _fail(f"Python {py.major}.{py.minor} — need 3.9 or newer")
        return 1

    missing = []
    for mod in ("torch", "torchvision", "open_clip", "matplotlib", "PIL"):
        try:
            m = __import__(mod)
            ver = getattr(m, "__version__", "?")
            _ok(f"{mod} {ver}")
        except ImportError:
            _fail(f"{mod} not installed")
            missing.append(mod)

    if missing:
        print()
        pkgs = {
            "torch": "torch",
            "torchvision": "torchvision",
            "open_clip": "open_clip_torch",
            "matplotlib": "matplotlib",
            "PIL": "pillow",
        }
        print("To fix, run:")
        print(f"  pip install {' '.join(pkgs[m] for m in missing)}")
        return 1

    import torch  # noqa: E402

    if torch.cuda.is_available():
        _ok(f"GPU: {torch.cuda.get_device_name(0)} — training will be fast")
    elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        _ok("Apple GPU (MPS) available — training will be reasonably fast")
    else:
        _note("No GPU — that's fine; the small models here train on CPU in minutes")

    print()
    print("All set. First run of each script will download model weights")
    print("(10-75 MB for training models, ~350 MB once for zero-shot CLIP).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
