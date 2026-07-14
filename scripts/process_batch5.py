#!/usr/bin/env python3
"""Process Batch 5 Burger Assembly & Build Flow.

Downloads generated PNGs from map results, flags any not at 1440x2560,
converts app-facing copies to WebP, archives PNG masters, writes metadata
YAMLs, appends the registry to AssetBible.md, and writes a batch manifest.
"""
import csv
import json
import os
import urllib.request
from PIL import Image

REPO = '/home/ubuntu/burger-mastery-assets'
RESULT_FILES = [
    '/home/ubuntu/generate_batch5_sections_abc.json',
    '/home/ubuntu/generate_batch5_sections_def.json',
]

TITLES_GOALS = {
    'BM-ASM-001': ('Toasted Brioche Bottom Bun', 'Recognize the toasted brioche foundation'),
    'BM-ASM-002': ('Toasted Potato Bottom Bun', 'Recognize the toasted potato bun foundation'),
    'BM-ASM-003': ('Correct Butter Coverage', 'Apply even butter coverage after toasting'),
    'BM-ASM-004': ('Golden Toast Comparison', 'Recognize perfect golden toast vs under and over'),
    'BM-ASM-005': ('Under-Toasted Bun', 'Recognize an under-toasted bun'),
    'BM-ASM-006': ('Over-Toasted Bun', 'Recognize an over-toasted bun'),
    'BM-ASM-007': ('Toasted Surface Macro', 'Checkpoint for ideal toasted surface texture'),
    'BM-ASM-008': ('Bottom Bun Ready', 'The foundation ready for assembly'),
    'BM-ASM-009': ('Correct Mayonnaise Spread', 'Apply mayonnaise correctly'),
    'BM-ASM-010': ('Correct Burger Sauce Spread', 'Apply burger sauce correctly'),
    'BM-ASM-011': ('Correct Mustard Spread', 'Apply mustard correctly'),
    'BM-ASM-012': ('Correct Ketchup Spread', 'Apply ketchup correctly'),
    'BM-ASM-013': ('Too Much Sauce', 'Recognize excessive sauce'),
    'BM-ASM-014': ('Too Little Sauce', 'Recognize insufficient sauce'),
    'BM-ASM-015': ('Even Sauce Coverage Macro', 'Checkpoint for even sauce coverage'),
    'BM-ASM-016': ('Sauced Bun Ready', 'Sauced base ready for toppings'),
    'BM-ASM-017': ('Correct Lettuce Placement', 'Place lettuce correctly'),
    'BM-ASM-018': ('Correct Tomato Placement', 'Place tomato correctly'),
    'BM-ASM-019': ('Correct Onion Placement', 'Place onion correctly'),
    'BM-ASM-020': ('Correct Pickle Placement', 'Place pickles correctly'),
    'BM-ASM-021': ('Complete Vegetable Stack', 'The complete vegetable foundation'),
    'BM-ASM-022': ('Uneven Vegetable Stack', 'Recognize an uneven stack'),
    'BM-ASM-023': ('Clean Layering Macro', 'Checkpoint for clean layering'),
    'BM-ASM-024': ('Vegetables Ready for Patty', 'Vegetable base ready for the patty'),
    'BM-ASM-025': ('Patty onto Vegetables', 'Place the cooked patty onto the vegetables'),
    'BM-ASM-026': ('Perfect Cheese Alignment', 'Align the cheese slice perfectly'),
    'BM-ASM-027': ('Centered Burger Stack', 'Keep the stack on one vertical axis'),
    'BM-ASM-028': ('Off-Centre Patty Mistake', 'Recognize an off-centre patty'),
    'BM-ASM-029': ('Double Patty Alignment', 'Align a double patty build'),
    'BM-ASM-030': ('Triple Stack Alignment', 'Align a triple stack build'),
    'BM-ASM-031': ('Melted Cheese Drape Macro', 'Checkpoint for the perfect cheese drape'),
    'BM-ASM-032': ('Stack Ready for Top Bun', 'The stack ready for the top bun'),
    'BM-ASM-033': ('Correct Top Bun Placement', 'Place the top bun squarely'),
    'BM-ASM-034': ('Slight Press After Assembly', 'Settle the stack with a gentle press'),
    'BM-ASM-035': ('Burger Held Naturally', 'Hold the burger correctly'),
    'BM-ASM-036': ('Burger Side Profile', 'The ideal finished profile'),
    'BM-ASM-037': ('Perfect Top-Down View', 'The finished top-down view'),
    'BM-ASM-038': ('Perfect 45-Degree View', 'The finished 45-degree view'),
    'BM-ASM-039': ('Finished Stack Macro', 'The finished stack up close'),
    'BM-ASM-040': ('Completed Burger Ready', 'The completed burger ready for serving'),
    'BM-HERO-ASM-001': ('Classic Cheeseburger Hero', 'The definitive classic cheeseburger'),
    'BM-HERO-ASM-002': ('Smash Burger Hero', 'The definitive smash burger'),
    'BM-HERO-ASM-003': ('Steakhouse Burger Hero', 'The definitive steakhouse burger'),
    'BM-HERO-ASM-004': ('High-Protein Burger Hero', 'The definitive high-protein build'),
    'BM-HERO-ASM-005': ('Meal-Prep Burger Hero', 'The meal-prep result'),
    'BM-HERO-ASM-006': ('Lower-Calorie Burger Hero', 'The definitive lower-calorie build'),
    'BM-HERO-ASM-007': ('Burger Cross-Section Hero', 'The definitive cross-section'),
    'BM-HERO-ASM-008': ('Editorial Beauty Shot', 'The signature homepage image'),
    'BM-HERO-ASM-009': ('Burger Held in One Hand', 'The burger in hand'),
    'BM-HERO-ASM-010': ('Minimalist Plated Hero', 'The minimalist plated presentation'),
}


def asset_key(slug):
    parts = slug.split('-')
    for i, p in enumerate(parts):
        if p.isdigit() and len(p) == 3:
            return '-'.join(parts[:i + 1])
    raise ValueError(slug)


def main():
    assets = []
    for fp in RESULT_FILES:
        with open(fp) as f:
            data = json.load(f)
        for r in data['results']:
            out = r.get('output') or {}
            sid = (out.get('asset_id') or '').strip()
            url = out.get('image')
            assert sid and url, f'missing output: {r.get("input", "")[:60]}'
            assets.append((sid, url))

    assert len(assets) == 50, f'expected 50, got {len(assets)}'
    keys = [asset_key(s) for s, _ in assets]
    assert len(set(keys)) == 50, 'duplicate asset ids'

    rows, lowres = [], []
    for sid, url in sorted(assets):
        key = asset_key(sid)
        hero = key.startswith('BM-HERO-ASM')
        rel_folder = 'images/heroes' if hero else 'images/assembly'
        webp_dir = os.path.join(REPO, rel_folder)
        arch_dir = os.path.join(REPO, 'archive', 'originals', rel_folder.replace('images/', ''))
        meta_dir = os.path.join(REPO, 'metadata', 'batch5')
        for d in (webp_dir, arch_dir, meta_dir):
            os.makedirs(d, exist_ok=True)

        png_path = os.path.join(arch_dir, sid + '.png')
        urllib.request.urlretrieve(url, png_path)
        img = Image.open(png_path)
        if img.size != (1440, 2560):
            lowres.append((sid, img.size))

        webp_path = os.path.join(webp_dir, sid + '.webp')
        quality = 92 if hero else 86
        img.save(webp_path, 'WEBP', quality=quality, method=6)
        if os.path.getsize(webp_path) > 900 * 1024:
            img.save(webp_path, 'WEBP', quality=quality - 6, method=6)

        title, goal = TITLES_GOALS[key]
        category = rel_folder.replace('images/', '')
        with open(os.path.join(meta_dir, key + '.yaml'), 'w') as f:
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
                f'prompt_source: Batch 5 brief (Pasted_content_05.txt)\n'
                f'approval_notes: Generated per Creative Director Batch 5 specification\n'
            )

        rows.append({
            'asset_id': key, 'title': title, 'category': category,
            'filename': sid + '.webp', 'goal': goal,
            'dims': f'{img.size[0]}x{img.size[1]}',
            'webp_kb': round(os.path.getsize(webp_path) / 1024),
        })

    lines = [
        '',
        '## Asset Registry — Batch 5: Burger Assembly & Build Flow',
        '',
        '| Asset ID | Title | Category | Filename | Status | Teaching Goal | Used In | Reuse Count | Version | Prompt Source | Approval Notes |',
        '|---|---|---|---|---|---|---|---|---|---|---|',
    ]
    for r in rows:
        lines.append(
            f'| {r["asset_id"]} | {r["title"]} | {r["category"]} | `{r["filename"]}` | approved | {r["goal"]} | [] | 0 | 1.0 | Batch 5 brief (Pasted_content_05.txt) | Generated per Creative Director Batch 5 specification |'
        )
    lines.append('')
    with open(os.path.join(REPO, 'docs', 'AssetBible.md'), 'a') as f:
        f.write('\n'.join(lines))

    with open(os.path.join(REPO, 'metadata', 'batch5_manifest.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f'processed {len(rows)} assets')
    print('LOW-RES NEEDING REGEN:', lowres if lowres else 'none')
    print('webp KB: min', min(r['webp_kb'] for r in rows), 'max', max(r['webp_kb'] for r in rows))


if __name__ == '__main__':
    main()
