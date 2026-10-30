#!/usr/bin/env python3
"""Build only the public static web output into dist/ for static hosting.

The repo also contains automation, tests and review reports that must not be
published with the public site. Run: python3 scripts/build_dist.py
"""
from __future__ import annotations
import json
import shutil
import subprocess
import sys
from pathlib import Path
from validate_ads_config import load_and_validate
from adsense_identity import ADS_TXT_LINE

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
               'regions.json', 'notice-watch.json', 'auto-notices.json', 'ads-config.json')
(DIST/'data').mkdir()
for filename in public_json:
    shutil.copyfile(ROOT / 'data' / filename, DIST / 'data' / filename)
ads_config = load_and_validate()
# Public authorized-seller declaration supports AdSense ownership preparation,
# independently of whether advertisements have been enabled or approved.
# Do not load Google advertising scripts merely to publish ads.txt.
(DIST/'ads.txt').write_text(ADS_TXT_LINE, encoding='utf-8')

# Render each format inside its own ad-document so atOptions cannot collide.
# A visitor-facing iframe is inserted only after they opt into advertising.
if ads_config.get('cloudflareBanners', {}).get('enabled') is True:
    ad_dir = DIST / 'ad-units'
    ad_dir.mkdir()
    for name, unit in ads_config['cloudflareBanners']['units'].items():
        options = {'key': unit['key'], 'format': 'iframe',
                   'height': unit['height'], 'width': unit['width'], 'params': {}}
        script = '<script>var atOptions = '+json.dumps(options, separators=(',',':'))+';</script>'
        script += '<script src="'+unit['scriptUrl']+'"></script>'
        page = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
                '<meta name="robots" content="noindex,nofollow">'
                '<style>html,body{margin:0;padding:0;overflow:hidden;background:transparent}</style>'
                '</head><body>') + script + '</body></html>'
        (ad_dir/(name+'.html')).write_text(page, encoding='utf-8')
print(f'Generated dist/ with {len(page_data)} pages; automation and private review reports excluded.')
