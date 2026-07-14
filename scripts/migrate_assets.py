#!/usr/bin/env python3
"""Migrate Burger Mastery photography assets into the asset repository.

Renames source PNGs to the official BM-<CATEGORY>-<NUMBER>-<slug> convention,
converts app-facing copies to WebP in images/<category>/, archives the original
PNG masters in archive/originals/<category>/, and emits a migration manifest CSV.
"""
import csv
import os
import shutil
from PIL import Image

REPO = '/home/ubuntu/burger-mastery-assets'
B1 = '/home/ubuntu/burger_mastery'
B2 = '/home/ubuntu/burger_mastery/batch2'
B3 = '/home/ubuntu/burger_mastery/batch3'

# (source_path, category_folder, BM filename base, hero_quality)
MAPPING = [
    # Batch 1 -> images/meat/ (MEAT 001-008)
    (f'{B1}/photo_1_premium_ground_beef.png',  'meat', 'BM-MEAT-001-beef-hero', True),
    (f'{B1}/photo_2_ground_pork.png',          'meat', 'BM-MEAT-002-pork-hero', True),
    (f'{B1}/photo_3_ground_lamb.png',          'meat', 'BM-MEAT-003-lamb-hero', True),
    (f'{B1}/photo_4_comparison_three_bowls.png', 'meat', 'BM-MEAT-004-beef-pork-lamb-comparison', False),
    (f'{B1}/photo_5_correct_mixing.png',       'meat', 'BM-MEAT-005-correct-gentle-mixing', False),
    (f'{B1}/photo_6_overmixed_meat.png',       'meat', 'BM-MEAT-006-overmixed-meat-mistake', False),
    (f'{B1}/photo_7_perfect_texture_macro.png', 'meat', 'BM-MEAT-007-perfect-texture-macro', True),
    (f'{B1}/photo_8_ready_to_shape.png',       'meat', 'BM-MEAT-008-ready-to-shape', False),
    # Batch 2 -> images/patty/ (PATTY 001-008)
    (f'{B2}/photo_1_portioning_scale.png',     'patty', 'BM-PATTY-001-portioning-150g-scale', False),
    (f'{B2}/photo_2_correct_patty_shape.png',  'patty', 'BM-PATTY-002-correct-gentle-shaping', False),
    (f'{B2}/photo_3_overcompressed_patty.png', 'patty', 'BM-PATTY-003-overcompressed-mistake', False),
    (f'{B2}/photo_4_thumb_dimple.png',         'patty', 'BM-PATTY-004-thumb-dimple', False),
    (f'{B2}/photo_5_no_dimple.png',            'patty', 'BM-PATTY-005-no-dimple-comparison', False),
    (f'{B2}/photo_6_three_thicknesses.png',    'patty', 'BM-PATTY-006-three-thicknesses', False),
    (f'{B2}/photo_7_macro_edge_detail.png',    'patty', 'BM-PATTY-007-macro-edge-detail', True),
    (f'{B2}/photo_8_ready_for_cooking.png',    'patty', 'BM-PATTY-008-ready-for-cooking', False),
    # Batch 3 Section A + B -> images/cooking/ (COOK 001-020)
    (f'{B3}/photo_01_first_contact.png',       'cooking', 'BM-COOK-001-first-contact', False),
    (f'{B3}/photo_02_fifteen_seconds.png',     'cooking', 'BM-COOK-002-fifteen-seconds-sear', False),
    (f'{B3}/photo_03_first_crust.png',         'cooking', 'BM-COOK-003-first-crust-forming', False),
    (f'{B3}/photo_04_ideal_flip_timing.png',   'cooking', 'BM-COOK-004-ideal-flip-timing', False),
    (f'{B3}/photo_05_freshly_flipped.png',     'cooking', 'BM-COOK-005-freshly-flipped', False),
    (f'{B3}/photo_06_second_side_crust.png',   'cooking', 'BM-COOK-006-second-side-crust', False),
    (f'{B3}/photo_07_finished_crust.png',      'cooking', 'BM-COOK-007-finished-crust', False),
    (f'{B3}/photo_08_macro_crust.png',         'cooking', 'BM-COOK-008-macro-crust-texture', True),
    (f'{B3}/photo_09_crosslight_crust.png',    'cooking', 'BM-COOK-009-crosslight-crust-detail', True),
    (f'{B3}/photo_10_perfect_no_cheese.png',   'cooking', 'BM-COOK-010-perfect-patty-no-cheese', True),
    (f'{B3}/photo_11_cold_pan.png',            'cooking', 'BM-COOK-011-cold-pan-mistake', False),
    (f'{B3}/photo_12_smoking_hot_pan.png',     'cooking', 'BM-COOK-012-smoking-hot-pan-mistake', False),
    (f'{B3}/photo_13_pale_crust.png',          'cooking', 'BM-COOK-013-pale-crust-mistake', False),
    (f'{B3}/photo_14_burnt_crust.png',         'cooking', 'BM-COOK-014-burnt-crust-mistake', False),
    (f'{B3}/photo_15_pressed_burger.png',      'cooking', 'BM-COOK-015-pressed-juices-mistake', False),
    (f'{B3}/photo_16_sticking_pan.png',        'cooking', 'BM-COOK-016-sticking-pan-mistake', False),
    (f'{B3}/photo_17_grey_exterior.png',       'cooking', 'BM-COOK-017-grey-exterior-mistake', False),
    (f'{B3}/photo_18_split_burger.png',        'cooking', 'BM-COOK-018-split-patty-mistake', False),
    (f'{B3}/photo_19_uneven_cooking.png',      'cooking', 'BM-COOK-019-uneven-cooking-mistake', False),
    (f'{B3}/photo_20_correct_vs_incorrect.png', 'cooking', 'BM-COOK-020-correct-vs-incorrect', False),
    # Batch 3 Section C -> images/cheese/ (CHEESE 001-010)
    (f'{B3}/photo_21_american_before.png',     'cheese', 'BM-CHEESE-001-american-before-melt', False),
    (f'{B3}/photo_22_american_melt.png',       'cheese', 'BM-CHEESE-002-perfect-american-melt', True),
    (f'{B3}/photo_23_cheddar_melt.png',        'cheese', 'BM-CHEESE-003-sharp-cheddar-melt', False),
    (f'{B3}/photo_24_swiss_melt.png',          'cheese', 'BM-CHEESE-004-swiss-melt', False),
    (f'{B3}/photo_25_provolone_melt.png',      'cheese', 'BM-CHEESE-005-provolone-melt', False),
    (f'{B3}/photo_26_pepperjack_melt.png',     'cheese', 'BM-CHEESE-006-pepper-jack-melt', False),
    (f'{B3}/photo_27_blue_softened.png',       'cheese', 'BM-CHEESE-007-blue-cheese-softened', False),
    (f'{B3}/photo_28_double_stack.png',        'cheese', 'BM-CHEESE-008-double-cheese-stack', False),
    (f'{B3}/photo_29_undermelted.png',         'cheese', 'BM-CHEESE-009-undermelted-mistake', False),
    (f'{B3}/photo_30_overmelted.png',          'cheese', 'BM-CHEESE-010-overmelted-mistake', False),
    # Batch 3 Section D -> images/cross-sections/ (XSEC 001-010)
    (f'{B3}/photo_31_rare.png',                'cross-sections', 'BM-XSEC-001-rare-cross-section', True),
    (f'{B3}/photo_32_medium_rare.png',         'cross-sections', 'BM-XSEC-002-medium-rare-cross-section', True),
    (f'{B3}/photo_33_medium.png',              'cross-sections', 'BM-XSEC-003-medium-cross-section', True),
    (f'{B3}/photo_34_medium_well.png',         'cross-sections', 'BM-XSEC-004-medium-well-cross-section', True),
    (f'{B3}/photo_35_well_done.png',           'cross-sections', 'BM-XSEC-005-well-done-cross-section', True),
    (f'{B3}/photo_36_rare_vs_mediumrare.png',  'cross-sections', 'BM-XSEC-006-rare-vs-medium-rare', True),
    (f'{B3}/photo_37_medium_vs_well.png',      'cross-sections', 'BM-XSEC-007-medium-vs-well-done', True),
    (f'{B3}/photo_38_juicy_macro.png',         'cross-sections', 'BM-XSEC-008-juicy-interior-macro', True),
    (f'{B3}/photo_39_dry_macro.png',           'cross-sections', 'BM-XSEC-009-dry-interior-macro', True),
    (f'{B3}/photo_40_resting_juices.png',      'cross-sections', 'BM-XSEC-010-resting-juices', True),
    # Batch 3 Section E -> images/heroes/ (HERO 001-010)
    (f'{B3}/photo_41_cooked_on_parchment.png', 'heroes', 'BM-HERO-001-cooked-patty-parchment', True),
    (f'{B3}/photo_42_cooked_with_cheese.png',  'heroes', 'BM-HERO-002-cooked-patty-cheese', True),
    (f'{B3}/photo_43_side_profile.png',        'heroes', 'BM-HERO-003-side-profile', True),
    (f'{B3}/photo_44_macro_crust_edge.png',    'heroes', 'BM-HERO-004-macro-crust-edge', True),
    (f'{B3}/photo_45_topdown_hero.png',        'heroes', 'BM-HERO-005-topdown-hero', True),
    (f'{B3}/photo_46_45degree_hero.png',       'heroes', 'BM-HERO-006-45-degree-hero', True),
    (f'{B3}/photo_47_holding_patty.png',       'heroes', 'BM-HERO-007-holding-cooked-patty', True),
    (f'{B3}/photo_48_stack_of_three.png',      'heroes', 'BM-HERO-008-stack-of-three', True),
    (f'{B3}/photo_49_ready_for_assembly.png',  'heroes', 'BM-HERO-009-ready-for-assembly', True),
    (f'{B3}/photo_50_editorial_hero.png',      'heroes', 'BM-HERO-010-signature-editorial-hero', True),
]


def human(n):
    return f'{n/1024:.0f} KB' if n < 1024**2 else f'{n/1024**2:.2f} MB'


def main():
    rows = []
    for src, cat, base, hero in MAPPING:
        assert os.path.exists(src), f'missing source: {src}'
        img = Image.open(src)
        ow, oh = img.size
        osize = os.path.getsize(src)

        webp_dir = os.path.join(REPO, 'images', cat)
        arch_dir = os.path.join(REPO, 'archive', 'originals', cat)
        os.makedirs(webp_dir, exist_ok=True)
        os.makedirs(arch_dir, exist_ok=True)

        webp_path = os.path.join(webp_dir, base + '.webp')
        arch_path = os.path.join(arch_dir, base + '.png')

        # Quality ladder: heroes/details higher; step down only if far above target size
        quality = 92 if hero else 86
        img.save(webp_path, 'WEBP', quality=quality, method=6)
        if os.path.getsize(webp_path) > 900 * 1024:
            img.save(webp_path, 'WEBP', quality=quality - 6, method=6)

        shutil.copy2(src, arch_path)

        nimg = Image.open(webp_path)
        rows.append({
            'original_filename': os.path.basename(src),
            'new_filename': base + '.webp',
            'destination_folder': f'images/{cat}/',
            'original_format': 'PNG',
            'new_format': 'WebP',
            'original_dimensions': f'{ow}x{oh}',
            'final_dimensions': f'{nimg.size[0]}x{nimg.size[1]}',
            'original_file_size': human(osize),
            'final_file_size': human(os.path.getsize(webp_path)),
            'status': 'migrated',
        })

    os.makedirs(os.path.join(REPO, 'metadata'), exist_ok=True)
    manifest = os.path.join(REPO, 'metadata', 'migration_manifest.csv')
    with open(manifest, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f'migrated {len(rows)} assets; manifest at {manifest}')


if __name__ == '__main__':
    main()
