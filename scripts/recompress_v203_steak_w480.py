#!/usr/bin/env python3
"""v2.0.3 — Recompress steak + soup w480 derived variants harder.

The natural hand-shot steak set carries film grain that webp compresses poorly:
w480 files average 51 KB (some 78 KB) vs 43 KB for burger heroes. Cards render
at <=360 CSS px so we can compress w480 harder (q55) with a light denoise-free
pipeline. Target <=40 KB per file. Sources: archive/png-masters/{steak,sides}.
"""
from PIL import Image
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOBS = [
    ("archive/png-masters/steak", "images/derived/w480/steak"),
    ("archive/png-masters/sides", "images/derived/w480/sides"),
]

for src_dir, out_dir in JOBS:
    src_abs = os.path.join(REPO, src_dir)
    out_abs = os.path.join(REPO, out_dir)
    if not os.path.isdir(src_abs):
        continue
    os.makedirs(out_abs, exist_ok=True)
    for name in sorted(os.listdir(src_abs)):
        if not name.lower().endswith(".png"):
            continue
        if "sides" in src_dir and "MM-SIDE-007" not in name:
            continue  # only the new soup photo; burger sides already fine
        im = Image.open(os.path.join(src_abs, name)).convert("RGB")
        w, h = im.size
        nw = 480
        nh = int(h * nw / w)
        r = im.resize((nw, nh), Image.LANCZOS)
        out = os.path.join(out_abs, name.replace(".png", ".webp"))
        # binary search quality to hit <=40 KB, floor q=45
        for q in (55, 50, 45):
            r.save(out, "WEBP", quality=q, method=6)
            if os.path.getsize(out) <= 40 * 1024:
                break
        print(f"{out}: {os.path.getsize(out)//1024} KB (q={q})")
