#!/usr/bin/env python3
"""Process v0.9.0 Batch A: download 32 generated images, QA, convert to WebP,
archive PNG masters, and place into the specified repository folders."""
import json, os, sys, csv
import urllib.request
from PIL import Image

REPO = "/home/ubuntu/burger-mastery-assets"
RESULTS = "/home/ubuntu/generate_v090_batch_a.json"
TMP = "/home/ubuntu/burger_mastery/v090_batch_a"
os.makedirs(TMP, exist_ok=True)

# Folder mapping per spec (asset_id -> images subfolder)
FOLDER = {
    "BM-MEAT-CHICKEN-001": "meat",
    "BM-MEAT-CHICKEN-002": "meat",
    "BM-MEAT-CHICKEN-003": "patty",
    "BM-MEAT-CHICKEN-004": "cooking",
    "BM-MEAT-CHICKEN-005": "heroes",
    "BM-MEAT-CHICKEN-006": "cross-sections",
    "BM-MEAT-CHICKEN-007": "cooking",
    "BM-MEAT-CHICKEN-008": "meat",
}
for i in range(1, 7):
    FOLDER[f"BM-ONION-{i:03d}"] = "flavours"
for i in range(1, 6):
    FOLDER[f"BM-GARLIC-{i:03d}"] = "flavours"
for i in range(1, 8):
    FOLDER[f"BM-SEASONING-{i:03d}"] = "flavours"
for h in ["BEEF", "PORK", "LAMB", "CHICKEN", "BEEFPORK", "BEEFLAMB"]:
    FOLDER[f"BM-HERO-{h}-PAIRING-001"] = "heroes"

HIGH_Q = {k for k in FOLDER if "HERO" in k or "CHICKEN-005" in k or "CHICKEN-006" in k}

with open(RESULTS) as f:
    data = json.load(f)["results"]

rows = []
errors = []
for r in data:
    out = r.get("output") or {}
    aid = (out.get("asset_id") or "").strip()
    url = out.get("image_file")
    if not aid or aid not in FOLDER:
        errors.append(f"Unknown/missing asset_id: {aid!r}")
        continue
    png_tmp = os.path.join(TMP, f"{aid}.png")
    if not os.path.exists(png_tmp):
        urllib.request.urlretrieve(url, png_tmp)
    im = Image.open(png_tmp)
    w, h = im.size
    status = "ok" if (w >= 1000 and h >= 1750 and abs(w / h - 9 / 16) < 0.05) else f"LOWRES_OR_RATIO {w}x{h}"
    # resize to canonical 1440x2560 if larger/other; keep if exact
    if (w, h) != (1440, 2560) and status == "ok":
        im = im.convert("RGB").resize((1440, 2560), Image.LANCZOS) if abs(w / h - 0.5625) < 0.01 else im
    sub = FOLDER[aid]
    prod_dir = os.path.join(REPO, "images", sub)
    arch_dir = os.path.join(REPO, "archive", "originals", sub)
    os.makedirs(prod_dir, exist_ok=True)
    os.makedirs(arch_dir, exist_ok=True)
    webp_path = os.path.join(prod_dir, f"{aid}.webp")
    q = 90 if aid in HIGH_Q else 84
    im.convert("RGB").save(webp_path, "WEBP", quality=q, method=6)
    # archive original PNG master untouched
    arch_path = os.path.join(arch_dir, f"{aid}.png")
    if not os.path.exists(arch_path):
        os.link(png_tmp, arch_path) if os.stat(png_tmp).st_dev == os.stat(arch_dir).st_dev else __import__("shutil").copy2(png_tmp, arch_path)
    wsz = os.path.getsize(webp_path)
    rows.append([aid, f"images/{sub}/{aid}.webp", f"{w}x{h}", f"{im.size[0]}x{im.size[1]}", f"{wsz//1024} KB", status])

rows.sort()
man = os.path.join(REPO, "metadata", "v090_batch_a_manifest.csv")
with open(man, "w", newline="") as f:
    wtr = csv.writer(f)
    wtr.writerow(["asset_id", "production_path", "source_dimensions", "final_dimensions", "webp_size", "status"])
    wtr.writerows(rows)

print(f"processed={len(rows)} errors={len(errors)}")
for e in errors:
    print("ERR:", e)
for row in rows:
    print(" | ".join(row))
