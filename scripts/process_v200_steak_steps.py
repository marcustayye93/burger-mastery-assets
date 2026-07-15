#!/usr/bin/env python3
"""Process v2.0.0 Meat Mastery steak step photography.
Converts staged PNGs to WebP masters under images/steak/ plus w480/w960
derived variants, archives the PNG masters, matching the established pipeline
(quality 92, method 6, <900KB guard).
"""
import os
import glob
import shutil
from PIL import Image

REPO = '/home/ubuntu/burger-mastery-assets'

def save_webp(img, path, quality):
    img.save(path, 'WEBP', quality=quality, method=6)
    if os.path.getsize(path) > 900 * 1024:
        img.save(path, 'WEBP', quality=quality - 6, method=6)

staged = sorted(glob.glob(os.path.join(REPO, 'staging', 'MM-STK-*.png')))
print(f'{len(staged)} staged steak images')
master_dir = os.path.join(REPO, 'images', 'steak')
os.makedirs(master_dir, exist_ok=True)
arch = os.path.join(REPO, 'archive', 'png-masters', 'steak')
os.makedirs(arch, exist_ok=True)

for src in staged:
    sid = os.path.splitext(os.path.basename(src))[0]
    img = Image.open(src).convert('RGB')
    save_webp(img, os.path.join(master_dir, sid + '.webp'), 92)
    for w in (480, 960):
        d = os.path.join(REPO, 'images', 'derived', f'w{w}', 'steak')
        os.makedirs(d, exist_ok=True)
        ratio = w / img.width
        var = img.resize((w, round(img.height * ratio)), Image.LANCZOS)
        save_webp(var, os.path.join(d, sid + '.webp'), 86)
    shutil.move(src, os.path.join(arch, sid + '.png'))
    print('done:', sid)
print('all processed')
