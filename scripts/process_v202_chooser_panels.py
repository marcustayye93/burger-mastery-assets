#!/usr/bin/env python3
"""v2.0.2 — Dedicated lightweight chooser panel images.

The diagonal split chooser needs two wide panels (full screen width, ~half screen
height). Deriving them from the existing hero masters:
  - MM-CHOOSER-BURGER-001 (burger card)  -> chooser-panel-burger
  - MM-HERO-STK-001 (steak hero)         -> chooser-panel-steak

Output: images/chooser/ at two widths, aggressively compressed:
  w720  (phones, ~16:10 panel)   target < 40 KB
  w360  (tiny/slow connections)  target < 15 KB
"""
from PIL import Image
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = {
    "chooser-panel-burger": os.path.join(REPO, "archive/png-masters/heroes/MM-CHOOSER-BURGER-001.png"),
    "chooser-panel-steak": os.path.join(REPO, "archive/png-masters/heroes/MM-HERO-STK-001-editorial-beauty-shot.png"),
}
OUT = os.path.join(REPO, "images/chooser")
os.makedirs(OUT, exist_ok=True)

# Panel aspect: width:height = 4:3 gives enough bleed for a half-screen
# diagonal panel on tall phones (screen ~ 390x844 -> panel ~ 390x460 incl. slant).
ASPECT = 4 / 3.4

for name, path in SRC.items():
    if not os.path.exists(path):
        # fall back to webp master in images/heroes
        alt = os.path.join(REPO, "images/heroes", os.path.basename(path).replace(".png", ".webp"))
        path = alt
    im = Image.open(path).convert("RGB")
    w, h = im.size
    # centre-crop to panel aspect
    target_h = int(w / ASPECT)
    if target_h <= h:
        top = (h - target_h) // 2
        im = im.crop((0, top, w, top + target_h))
    else:
        target_w = int(h * ASPECT)
        left = (w - target_w) // 2
        im = im.crop((left, 0, left + target_w, h))
    for width, q in ((720, 62), (360, 58)):
        r = im.resize((width, int(width / ASPECT)), Image.LANCZOS)
        out = os.path.join(OUT, f"{name}-w{width}.webp")
        r.save(out, "WEBP", quality=q, method=6)
        print(f"{out}: {os.path.getsize(out)//1024} KB {r.size}")
