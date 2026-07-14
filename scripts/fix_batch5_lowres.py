#!/usr/bin/env python3
"""Replace the two low-resolution Batch 5 assets with full-resolution regenerations."""
import csv
import os
import shutil
from PIL import Image

REPO = '/home/ubuntu/burger-mastery-assets'
FIX = '/home/ubuntu/burger_mastery/batch5_fix'

REPLACEMENTS = [
    ('BM-ASM-007-toasted-surface-macro', 'images/assembly', False),
    ('BM-ASM-020-correct-pickle-placement', 'images/assembly', False),
]

for slug, rel_folder, hero in REPLACEMENTS:
    src = os.path.join(FIX, slug + '.png')
    img = Image.open(src)
    assert img.size == (1440, 2560), f'{slug} wrong size {img.size}'
    arch = os.path.join(REPO, 'archive', 'originals', rel_folder.replace('images/', ''), slug + '.png')
    shutil.copy2(src, arch)
    webp = os.path.join(REPO, rel_folder, slug + '.webp')
    quality = 92 if hero else 86
    img.save(webp, 'WEBP', quality=quality, method=6)
    if os.path.getsize(webp) > 900 * 1024:
        img.save(webp, 'WEBP', quality=quality - 6, method=6)
    print(slug, 'replaced;', Image.open(webp).size, round(os.path.getsize(webp)/1024), 'KB')

mf = os.path.join(REPO, 'metadata', 'batch5_manifest.csv')
with open(mf) as f:
    rows = list(csv.DictReader(f))
for r in rows:
    for slug, rel_folder, _ in REPLACEMENTS:
        if r['filename'] == slug + '.webp':
            r['dims'] = '1440x2560'
            r['webp_kb'] = str(round(os.path.getsize(os.path.join(REPO, rel_folder, slug + '.webp'))/1024))
with open(mf, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print('manifest updated')
