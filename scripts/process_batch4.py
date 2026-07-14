#!/usr/bin/env python3
"""Process Batch 4 Ingredient Foundation Library.

Downloads generated PNGs from map results, converts app-facing copies to WebP
in the specified images/ folders, archives PNG masters in archive/originals/,
writes one metadata YAML per asset, and appends the registry to AssetBible.md.
"""
import csv
import json
import os
import urllib.request
from PIL import Image

REPO = '/home/ubuntu/burger-mastery-assets'
RESULT_FILES = [
    '/home/ubuntu/generate_batch4_sections_abc.json',
    '/home/ubuntu/generate_batch4_sections_def.json',
]

# asset_id prefix -> (repo image folder, hero-quality flag)
FOLDERS = {
    'BM-ING-BEEF': ('images/ingredients/beef', False),
    'BM-CHEESE': ('images/cheese', False),
    'BM-BUN': ('images/ingredients/buns', False),
    'BM-VEG': ('images/ingredients/vegetables', False),
    'BM-COND': ('images/condiments', False),
    'BM-HERO-ING': ('images/heroes/ingredients', True),
}

TITLES_GOALS = {
    'BM-ING-BEEF-001': ('80/20 Ground Chuck', 'Recognize 80/20 chuck and its fat level'),
    'BM-ING-BEEF-002': ('85/15 Ground Chuck', 'Recognize 85/15 chuck and its fat level'),
    'BM-ING-BEEF-003': ('90/10 Lean Beef', 'Recognize 90/10 lean beef'),
    'BM-ING-BEEF-004': ('95/5 Extra Lean Beef', 'Recognize 95/5 extra lean beef'),
    'BM-ING-BEEF-005': ('Fat Percentage Comparison', 'Compare beef fat percentages side by side'),
    'BM-ING-BEEF-006': ('Fat Marbling Macro', 'Recognize quality fat marbling up close'),
    'BM-ING-BEEF-007': ('Loose Premium Grind', 'Recognize the ideal loose coarse grind'),
    'BM-ING-BEEF-008': ('Fine Grind Comparison', 'Distinguish coarse vs fine grind'),
    'BM-CHEESE-011': ('American Cheese Slices', 'Identify American cheese slices'),
    'BM-CHEESE-012': ('Sharp Cheddar Slices', 'Identify sharp cheddar slices'),
    'BM-CHEESE-013': ('Swiss Cheese', 'Identify Swiss cheese'),
    'BM-CHEESE-014': ('Provolone', 'Identify provolone'),
    'BM-CHEESE-015': ('Pepper Jack', 'Identify Pepper Jack'),
    'BM-CHEESE-016': ('Blue Cheese', 'Identify blue cheese'),
    'BM-CHEESE-017': ('Mozzarella', 'Identify fresh mozzarella'),
    'BM-CHEESE-018': ('Cheese Comparison Flat Lay', 'Compare all burger cheeses at a glance'),
    'BM-BUN-001': ('Brioche Bun', 'Identify a brioche bun'),
    'BM-BUN-002': ('Potato Bun', 'Identify a potato bun'),
    'BM-BUN-003': ('Sesame Bun', 'Identify a sesame bun'),
    'BM-BUN-004': ('Pretzel Bun', 'Identify a pretzel bun'),
    'BM-BUN-005': ('Ciabatta', 'Identify ciabatta'),
    'BM-BUN-006': ('English Muffin', 'Identify an English muffin'),
    'BM-BUN-007': ('Lettuce Wrap', 'Recognize the lettuce wrap alternative'),
    'BM-BUN-008': ('All Bun Comparison', 'Compare all bun options at a glance'),
    'BM-VEG-001': ('Tomato Slices', 'Identify ideal burger tomato slices'),
    'BM-VEG-002': ('Iceberg Lettuce', 'Identify iceberg lettuce'),
    'BM-VEG-003': ('Butter Lettuce', 'Identify butter lettuce'),
    'BM-VEG-004': ('Red Onion', 'Identify red onion'),
    'BM-VEG-005': ('White Onion', 'Identify white onion'),
    'BM-VEG-006': ('Pickles', 'Identify burger pickles'),
    'BM-VEG-007': ('Jalapenos', 'Identify jalapenos'),
    'BM-VEG-008': ('Vegetable Comparison', 'Compare all burger vegetables at a glance'),
    'BM-COND-001': ('Mayonnaise', 'Identify mayonnaise'),
    'BM-COND-002': ('Burger Sauce', 'Identify classic burger sauce'),
    'BM-COND-003': ('Yellow Mustard', 'Identify yellow mustard'),
    'BM-COND-004': ('Dijon Mustard', 'Identify Dijon mustard'),
    'BM-COND-005': ('Ketchup', 'Identify ketchup'),
    'BM-COND-006': ('BBQ Sauce', 'Identify BBQ sauce'),
    'BM-COND-007': ('Chipotle Mayo', 'Identify chipotle mayo'),
    'BM-COND-008': ('Greek Yoghurt Burger Sauce', 'Recognize the lighter yoghurt-based sauce'),
    'BM-HERO-ING-001': ('Classic Cheeseburger Layout', 'See everything needed for the classic cheeseburger'),
    'BM-HERO-ING-002': ('High-Protein Layout', 'See the high-protein build'),
    'BM-HERO-ING-003': ('Low-Calorie Layout', 'See the low-calorie build'),
    'BM-HERO-ING-004': ('Steakhouse Layout', 'See the steakhouse build'),
    'BM-HERO-ING-005': ('Smash Burger Layout', 'See the smash burger build'),
    'BM-HERO-ING-006': ('Meal-Prep Layout', 'See batch preparation made visual'),
    'BM-HERO-ING-007': ('Beef vs Beef-Pork Comparison', 'Compare beef vs beef-pork blend'),
    'BM-HERO-ING-008': ('Beef vs Beef-Lamb Comparison', 'Compare beef vs beef-lamb blend'),
}


def asset_key(asset_id_slug):
    """BM-ING-BEEF-001-80-20-ground-chuck -> BM-ING-BEEF-001"""
    parts = asset_id_slug.split('-')
    for i, p in enumerate(parts):
        if p.isdigit() and len(p) == 3:
            return '-'.join(parts[:i + 1])
    raise ValueError(f'no numeric id in {asset_id_slug}')


def folder_for(key):
    for prefix in sorted(FOLDERS, key=len, reverse=True):
        if key.startswith(prefix):
            return FOLDERS[prefix]
    raise ValueError(f'no folder for {key}')


def main():
    assets = []
    for fp in RESULT_FILES:
        with open(fp) as f:
            data = json.load(f)
        for r in data['results']:
            out = r.get('output') or {}
            sid = (out.get('asset_id') or '').strip()
            url = out.get('image')
            assert sid and url, f'missing output in {fp}: {r.get("input", "")[:60]}'
            assets.append((sid, url))

    assert len(assets) == 48, f'expected 48 assets, got {len(assets)}'
    ids = [asset_key(s) for s, _ in assets]
    assert len(set(ids)) == 48, 'duplicate asset ids detected'

    rows = []
    for sid, url in sorted(assets):
        key = asset_key(sid)
        rel_folder, hero = folder_for(key)
        webp_dir = os.path.join(REPO, rel_folder)
        arch_dir = os.path.join(REPO, 'archive', 'originals', rel_folder.replace('images/', ''))
        meta_dir = os.path.join(REPO, 'metadata', 'batch4')
        for d in (webp_dir, arch_dir, meta_dir):
            os.makedirs(d, exist_ok=True)

        png_path = os.path.join(arch_dir, sid + '.png')
        urllib.request.urlretrieve(url, png_path)

        img = Image.open(png_path)
        ow, oh = img.size
        webp_path = os.path.join(webp_dir, sid + '.webp')
        quality = 92 if hero else 86
        img.save(webp_path, 'WEBP', quality=quality, method=6)
        if os.path.getsize(webp_path) > 900 * 1024:
            img.save(webp_path, 'WEBP', quality=quality - 6, method=6)

        title, goal = TITLES_GOALS[key]
        category = rel_folder.replace('images/', '')
        yaml_path = os.path.join(meta_dir, key + '.yaml')
        with open(yaml_path, 'w') as f:
            f.write(
                f'id: {key}\n'
                f'title: {title}\n'
                f'category: {category}\n'
                f'filename: {sid}.webp\n'
                f'status: approved\n'
                f'teaching_goal: {goal}\n'
                f'used_in: []\n'
                f'reuse_count: 0\n'
                f'version: 1.0\n'
                f'prompt_source: Batch 4 brief (Pasted_content_04.txt)\n'
                f'approval_notes: Generated per Creative Director Batch 4 specification\n'
            )

        rows.append({
            'asset_id': key, 'title': title, 'category': category,
            'filename': sid + '.webp', 'goal': goal,
            'dims': f'{ow}x{oh}',
            'webp_kb': round(os.path.getsize(webp_path) / 1024),
        })

    # Append registry to AssetBible.md
    lines = [
        '',
        '## Asset Registry — Batch 4: Ingredient Foundation Library',
        '',
        '| Asset ID | Title | Category | Filename | Status | Teaching Goal | Used In | Reuse Count | Version | Prompt Source | Approval Notes |',
        '|---|---|---|---|---|---|---|---|---|---|---|',
    ]
    for r in rows:
        lines.append(
            f'| {r["asset_id"]} | {r["title"]} | {r["category"]} | `{r["filename"]}` | approved | {r["goal"]} | [] | 0 | 1.0 | Batch 4 brief (Pasted_content_04.txt) | Generated per Creative Director Batch 4 specification |'
        )
    lines.append('')
    with open(os.path.join(REPO, 'docs', 'AssetBible.md'), 'a') as f:
        f.write('\n'.join(lines))

    with open(os.path.join(REPO, 'metadata', 'batch4_manifest.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f'processed {len(rows)} assets')
    print('dims check:', set(r['dims'] for r in rows))
    print('webp sizes KB: min', min(r['webp_kb'] for r in rows), 'max', max(r['webp_kb'] for r in rows))


if __name__ == '__main__':
    main()
