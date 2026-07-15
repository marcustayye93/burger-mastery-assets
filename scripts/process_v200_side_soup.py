#!/usr/bin/env python3
"""Process MM-SIDE-007 beef ribs soup photo into images/sides/ + derived variants."""
import os
import shutil
from PIL import Image

REPO = '/home/ubuntu/burger-mastery-assets'
SID = 'MM-SIDE-007-beef-ribs-soup'

def save_webp(img, path, quality):
    img.save(path, 'WEBP', quality=quality, method=6)
    if os.path.getsize(path) > 900 * 1024:
        img.save(path, 'WEBP', quality=quality - 6, method=6)

src = os.path.join(REPO, 'staging', SID + '.png')
img = Image.open(src).convert('RGB')
master_dir = os.path.join(REPO, 'images', 'sides')
os.makedirs(master_dir, exist_ok=True)
save_webp(img, os.path.join(master_dir, SID + '.webp'), 92)
for w in (480, 960):
    d = os.path.join(REPO, 'images', 'derived', f'w{w}', 'sides')
    os.makedirs(d, exist_ok=True)
    ratio = w / img.width
    var = img.resize((w, round(img.height * ratio)), Image.LANCZOS)
    save_webp(var, os.path.join(d, SID + '.webp'), 86)
arch = os.path.join(REPO, 'archive', 'png-masters', 'sides')
os.makedirs(arch, exist_ok=True)
shutil.move(src, os.path.join(arch, SID + '.png'))
print('done:', SID)
