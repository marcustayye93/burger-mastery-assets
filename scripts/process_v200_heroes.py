#!/usr/bin/env python3
"""Process v2.0.0 Meat Mastery hero/chooser images.
Converts staged PNGs to WebP masters under images/heroes/ plus w480/w960
derived variants, archives the PNG masters, matching the established pipeline
(hero quality 92, method 6, <900KB guard).
"""
import os
import shutil
from PIL import Image

REPO = '/home/ubuntu/burger-mastery-assets'
ITEMS = [
    'MM-HERO-STK-001-editorial-beauty-shot',
    'MM-CHOOSER-BURGER-001',
]

def save_webp(img, path, quality):
    img.save(path, 'WEBP', quality=quality, method=6)
    if os.path.getsize(path) > 900 * 1024:
        img.save(path, 'WEBP', quality=quality - 6, method=6)

for sid in ITEMS:
    src = os.path.join(REPO, 'staging', sid + '.png')
    img = Image.open(src).convert('RGB')
    print(sid, 'source', img.size)
    # master webp
    master_dir = os.path.join(REPO, 'images', 'heroes')
    save_webp(img, os.path.join(master_dir, sid + '.webp'), 92)
    # derived variants
    for w in (480, 960):
        d = os.path.join(REPO, 'images', 'derived', f'w{w}', 'heroes')
        os.makedirs(d, exist_ok=True)
        ratio = w / img.width
        var = img.resize((w, round(img.height * ratio)), Image.LANCZOS)
        save_webp(var, os.path.join(d, sid + '.webp'), 86)
    # archive png master
    arch = os.path.join(REPO, 'archive', 'png-masters', 'heroes')
    os.makedirs(arch, exist_ok=True)
    shutil.move(src, os.path.join(arch, sid + '.png'))
    print(' done:', sid)

print('all processed')
