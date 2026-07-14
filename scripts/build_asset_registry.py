#!/usr/bin/env python3
"""Append the asset registry table to docs/AssetBible.md from the migration manifest."""
import csv
import os

REPO = '/home/ubuntu/burger-mastery-assets'

TEACHING_GOALS = {
    'BM-MEAT-001': ('Premium Ground Beef Hero', 'Recognize quality 80/20 chuck with proper marbling'),
    'BM-MEAT-002': ('Ground Pork Hero', 'Identify pork colour and fat texture vs beef'),
    'BM-MEAT-003': ('Ground Lamb Hero', 'Identify lamb colour and coarser grind'),
    'BM-MEAT-004': ('Meat Comparison', 'Compare beef, pork and lamb side by side'),
    'BM-MEAT-005': ('Correct Gentle Mixing', 'Fold meat gently without squeezing'),
    'BM-MEAT-006': ('Overmixed Meat Mistake', 'Recognize dense sticky overmixed meat'),
    'BM-MEAT-007': ('Perfect Texture Macro', 'Visual checkpoint for ideal mix texture'),
    'BM-MEAT-008': ('Ready to Shape', 'Recognize a finished rested mixture'),
    'BM-PATTY-001': ('Portioning at 150 g', 'Portion patties at the correct weight'),
    'BM-PATTY-002': ('Correct Gentle Shaping', 'Shape with light pressure and loose texture'),
    'BM-PATTY-003': ('Over-Compressed Mistake', 'Recognize a too-tightly packed patty'),
    'BM-PATTY-004': ('Thumb Dimple', 'Dimple the centre so patties stay flat'),
    'BM-PATTY-005': ('No Dimple Comparison', 'Direct comparison against the dimpled patty'),
    'BM-PATTY-006': ('Three Thicknesses', 'Distinguish smash, standard and steakhouse thickness'),
    'BM-PATTY-007': ('Macro Edge Detail', 'Visual checkpoint for a properly shaped edge'),
    'BM-PATTY-008': ('Ready for Cooking', 'Transition asset into the Cooking chapter'),
    'BM-COOK-001': ('First Contact', 'Correct first contact with a preheated pan'),
    'BM-COOK-002': ('Fifteen Seconds Sear', 'What the sear looks like at 15 seconds'),
    'BM-COOK-003': ('First Crust Forming', 'Beginning of proper crust formation'),
    'BM-COOK-004': ('Ideal Flip Timing', 'Exactly when to flip the patty'),
    'BM-COOK-005': ('Freshly Flipped', 'A properly seared first side after flipping'),
    'BM-COOK-006': ('Second Side Crust', 'Finishing the second side properly'),
    'BM-COOK-007': ('Finished Crust', 'The finished perfect crust in pan'),
    'BM-COOK-008': ('Macro Crust Texture', 'Visual checkpoint of ideal crust texture'),
    'BM-COOK-009': ('Crosslight Crust Detail', 'Crust relief revealed by directional light'),
    'BM-COOK-010': ('Perfect Patty No Cheese', 'The complete correctly cooked patty'),
    'BM-COOK-011': ('Cold Pan Mistake', 'Never start in a cold pan'),
    'BM-COOK-012': ('Smoking Hot Pan Mistake', 'Danger of an overheated pan'),
    'BM-COOK-013': ('Pale Crust Mistake', 'Failed crust from insufficient heat'),
    'BM-COOK-014': ('Burnt Crust Mistake', 'Burnt crust from excessive heat or time'),
    'BM-COOK-015': ('Pressed Juices Mistake', 'Never press the patty'),
    'BM-COOK-016': ('Sticking Pan Mistake', 'Sticking from flipping too early'),
    'BM-COOK-017': ('Grey Exterior Mistake', 'Grey steamed exterior from overcrowding'),
    'BM-COOK-018': ('Split Patty Mistake', 'Over-handling destroys the patty'),
    'BM-COOK-019': ('Uneven Cooking Mistake', 'Recognize uneven heat distribution'),
    'BM-COOK-020': ('Correct vs Incorrect', 'Correct vs incorrect result at a glance'),
    'BM-CHEESE-001': ('American Before Melt', 'American cheese at placement, before melting'),
    'BM-CHEESE-002': ('Perfect American Melt', 'The ideal American melt'),
    'BM-CHEESE-003': ('Sharp Cheddar Melt', 'How sharp cheddar melts differently'),
    'BM-CHEESE-004': ('Swiss Melt', 'The Swiss melt behaviour'),
    'BM-CHEESE-005': ('Provolone Melt', 'The provolone melt behaviour'),
    'BM-CHEESE-006': ('Pepper Jack Melt', 'The Pepper Jack melt behaviour'),
    'BM-CHEESE-007': ('Blue Cheese Softened', 'Blue cheese softens rather than melts flat'),
    'BM-CHEESE-008': ('Double Cheese Stack', 'The double-cheese technique'),
    'BM-CHEESE-009': ('Undermelted Mistake', 'Recognize undermelted cheese'),
    'BM-CHEESE-010': ('Overmelted Mistake', 'Recognize overmelted, split cheese'),
    'BM-XSEC-001': ('Rare Cross-Section', 'Identify rare doneness interior'),
    'BM-XSEC-002': ('Medium Rare Cross-Section', 'Identify medium rare interior'),
    'BM-XSEC-003': ('Medium Cross-Section', 'Identify medium interior'),
    'BM-XSEC-004': ('Medium Well Cross-Section', 'Identify medium well interior'),
    'BM-XSEC-005': ('Well Done Cross-Section', 'Identify well done interior'),
    'BM-XSEC-006': ('Rare vs Medium Rare', 'Compare rare and medium rare directly'),
    'BM-XSEC-007': ('Medium vs Well Done', 'Compare medium and well done directly'),
    'BM-XSEC-008': ('Juicy Interior Macro', 'What a juicy interior looks like up close'),
    'BM-XSEC-009': ('Dry Interior Macro', 'What a dry overcooked interior looks like'),
    'BM-XSEC-010': ('Resting Juices', 'Why resting the patty matters'),
    'BM-HERO-001': ('Cooked Patty on Parchment', 'Universal finished patty asset'),
    'BM-HERO-002': ('Cooked Patty with Cheese', 'Universal cheese-topped patty asset'),
    'BM-HERO-003': ('Side Profile', 'Ideal cooked patty profile and thickness'),
    'BM-HERO-004': ('Macro Crust Edge', 'Crust-to-interior transition checkpoint'),
    'BM-HERO-005': ('Top-Down Hero', 'Top-down universal hero asset'),
    'BM-HERO-006': ('45-Degree Hero', '45-degree universal hero asset'),
    'BM-HERO-007': ('Holding Cooked Patty', 'Craft-focused presentation of the patty'),
    'BM-HERO-008': ('Stack of Three', 'Multi-patty universal asset'),
    'BM-HERO-009': ('Ready for Assembly', 'Transition into the Assembly chapter'),
    'BM-HERO-010': ('Signature Editorial Hero', 'Definitive Burger Mastery signature image'),
}

PROMPT_SOURCES = {
    'MEAT': 'Batch 1 brief (Pasted_content.txt)',
    'PATTY': 'Batch 2 brief (Pasted_content_01.txt)',
    'COOK': 'Batch 3 brief (Pasted_content_02.txt)',
    'CHEESE': 'Batch 3 brief (Pasted_content_02.txt)',
    'XSEC': 'Batch 3 brief (Pasted_content_02.txt)',
    'HERO': 'Batch 3 brief (Pasted_content_02.txt)',
}


def main():
    manifest = os.path.join(REPO, 'metadata', 'migration_manifest.csv')
    with open(manifest) as f:
        rows = list(csv.DictReader(f))

    lines = [
        '',
        '## Asset Registry',
        '',
        'All assets below are approved production assets migrated from Batches 1-3. Reuse counts start at 0 and should be incremented as assets are placed in the application.',
        '',
        '| Asset ID | Title | Category | Filename | Status | Teaching Goal | Used In | Reuse Count | Version | Prompt Source | Approval Notes |',
        '|---|---|---|---|---|---|---|---|---|---|---|',
    ]
    for r in rows:
        base = r['new_filename'].replace('.webp', '')
        asset_id = '-'.join(base.split('-')[:3])
        cat_code = base.split('-')[1]
        category = r['destination_folder'].replace('images/', '').strip('/')
        title, goal = TEACHING_GOALS[asset_id]
        src = PROMPT_SOURCES[cat_code]
        lines.append(
            f'| {asset_id} | {title} | {category} | `{r["new_filename"]}` | approved | {goal} | [] | 0 | 1.0 | {src} | Approved in founder-reviewed batch delivery |'
        )
    lines.append('')

    bible = os.path.join(REPO, 'docs', 'AssetBible.md')
    with open(bible, 'a') as f:
        f.write('\n'.join(lines))
    print(f'registry appended: {len(rows)} assets')


if __name__ == '__main__':
    main()
