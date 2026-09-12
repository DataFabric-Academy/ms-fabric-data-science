"""Print Lab 0-2 notebook cell outlines for checklist."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path("labs/notebooks")
for name in [
    "00-environment-verification.ipynb",
    "01-explore-data.ipynb",
    "02-preprocess-data-wrangler.ipynb",
]:
    nb = json.loads((ROOT / name).read_text(encoding="utf-8"))
    print("==", name, "cells", len(nb["cells"]))
    for i, cell in enumerate(nb["cells"]):
        src = "".join(cell.get("source", []))
        first = src.strip().splitlines()[0][:100] if src.strip() else "(empty)"
        print(f"  [{i}] {cell['cell_type']:8} {first}")
