#!/usr/bin/env python3
"""Build only the public static web output into dist/ for Netlify.

The repo also contains automation, tests and review reports that must not be
published with the public site. Run: python3 scripts/build_dist.py
"""
from __future__ import annotations
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
subprocess.run([sys.executable, str(ROOT / 'scripts' / 'build_final.py')], cwd=ROOT, check=True)
if DIST.exists():
    shutil.rmtree(DIST)
DIST.mkdir()

# HTML routes enumerated in pages.json; never copy automation or hidden files.
page_data = json.loads((ROOT/'data'/'pages.json').read_text(encoding='utf-8'))
for page in page_data.values():
    src = ROOT / page['path'] / 'index.html' if page['path'] else ROOT / 'index.html'
    assert src.is_file(), f"Missing page route: {src}"
    dst = DIST / page['path'] / 'index.html' if page['path'] else DIST / 'index.html'
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)

for filename in ('robots.txt', 'sitemap.xml', 'googlefcd24aba957dc07b.html'):
    shutil.copyfile(ROOT / filename, DIST / filename)
shutil.copytree(ROOT / 'assets', DIST / 'assets')
public_json = ('jobs.json', 'sources.json', 'pages.json', 'exam-updates.json',
               'regions.json', 'notice-watch.json')
(DIST/'data').mkdir()
for filename in public_json:
    shutil.copyfile(ROOT / 'data' / filename, DIST / 'data' / filename)
print(f'Generated dist/ with {len(page_data)} pages; automation and private review reports excluded.')
