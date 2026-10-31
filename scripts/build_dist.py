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

# Render each format inside its own ad-document so atOptions cannot collide.
# A visitor-facing iframe is inserted only after they opt into advertising.
if ads_config.get('cloudflareBanners', {}).get('enabled') is True:
    verified_units = {name: unit for name, unit in ads_config['cloudflareBanners']['units'].items()
                      if unit.get('enabled') is True and unit.get('sourceVerified') is True}
    if verified_units:
        ad_dir = DIST / 'ad-units'
        ad_dir.mkdir()
    for name, unit in verified_units.items():
        options = {'key': unit['key'], 'format': 'iframe',
                   'height': unit['height'], 'width': unit['width'], 'params': {}}
        script = '<script>var atOptions = '+json.dumps(options, separators=(',',':'))+';</script>'
        script += '<script src="'+unit['scriptUrl']+'"></script>'
        # The banner must report genuine creative markup, not merely that the
        # empty wrapper document loaded. No filled markup => collapse in parent.
        probe = "<script>(function(){var unitName=UNIT_NAME,done=false;function report(state){if(done)return;done=true;window.parent.postMessage({type:'jobpath-banner-fill',unit:unitName,status:state},'https://jobpath-india.pages.dev');}function isVisible(node,minW,minH){var box=node.getBoundingClientRect();return box.width>=minW&&box.height>=minH&&getComputedStyle(node).visibility!=='hidden';}function creative(){var imgs=document.body.querySelectorAll('img');for(var i=0;i<imgs.length;i++){var im=imgs[i];if(im.complete&&im.naturalWidth>=90&&im.naturalHeight>=32&&isVisible(im,90,32))return true;}var videos=document.body.querySelectorAll('video');for(var j=0;j<videos.length;j++){if(videos[j].readyState>1&&isVisible(videos[j],90,32))return true;}var canvases=document.body.querySelectorAll('canvas');for(var k=0;k<canvases.length;k++){var canvas=canvases[k];if(canvas.width>=90&&canvas.height>=32&&isVisible(canvas,90,32))return true;}var links=document.body.querySelectorAll('a[href]');for(var m=0;m<links.length;m++){var link=links[m];if((link.textContent||'').trim().length>12&&isVisible(link,90,24))return true;}var frames=document.body.querySelectorAll('iframe');for(var z=0;z<frames.length;z++){var frame=frames[z],source=frame.getAttribute('src')||'';if(isVisible(frame,90,32)&&(source.indexOf('https://')===0||frame.getAttribute('srcdoc')))return true;try{if(isVisible(frame,90,32)&&frame.contentDocument&&frame.contentDocument.body&&frame.contentDocument.body.children.length>0)return true;}catch(e){}}return false;}function check(){if(!done&&creative())report('filled');}var obs=new MutationObserver(check);obs.observe(document.body,{childList:true,subtree:true,attributes:true,attributeFilter:['src','srcdoc','style','class']});window.addEventListener('load',check);setTimeout(check,450);setTimeout(check,1250);setTimeout(check,2300);setTimeout(function(){if(!done){check();if(!done)report('empty');obs.disconnect();}},4700);})();</script>"
        probe = probe.replace('UNIT_NAME', json.dumps(name))
        page = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
                '<meta name="robots" content="noindex,nofollow">'
                '<style>html,body{margin:0;padding:0;overflow:hidden;background:transparent}</style>'
                '</head><body>') + script + probe + '</body></html>'
        (ad_dir/(name+'.html')).write_text(page, encoding='utf-8')
print(f'Generated dist/ with {len(page_data)} pages; automation and private review reports excluded.')
