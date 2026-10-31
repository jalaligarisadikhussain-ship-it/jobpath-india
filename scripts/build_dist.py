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
               'regions.json', 'notice-watch.json', 'auto-notices.json', 'ads-config.json', 'editorial-pages.json')
(DIST/'data').mkdir()
for filename in public_json:
    shutil.copyfile(ROOT / 'data' / filename, DIST / 'data' / filename)
ads_config = load_and_validate()
# Public authorized-seller declaration supports AdSense ownership preparation,
# independently of whether advertisements have been enabled or approved.
# Do not load Google advertising scripts merely to publish ads.txt.
(DIST/'ads.txt').write_text(ADS_TXT_LINE, encoding='utf-8')

# Adsterra support explicitly prohibits embedding publisher ad code in custom
# iframes. Therefore publish NO ad-unit iframe wrappers. The original one
# native tag is rendered directly in assets/js/ads.mjs after privacy checks.
assert ads_config['cloudflareBanners']['enabled'] is False, 'Publisher iframe banners must stay disabled'
# Cloudflare Pages reads _headers. The approved original Native Banner script
# is inserted directly in the main document, never a custom publisher iframe.
(DIST/'_headers').write_text("""/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: DENY
  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()
  Content-Security-Policy: object-src 'none'; base-uri 'self'; frame-ancestors 'self'; form-action 'self'

/assets/*
  Cache-Control: public, max-age=600, must-revalidate

/data/*
  Cache-Control: public, max-age=300, must-revalidate
""", encoding='utf-8')

print(f'Generated dist/ with {len(page_data)} pages; automation and private review reports excluded.')
