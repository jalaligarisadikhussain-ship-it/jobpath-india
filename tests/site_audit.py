"""Offline static asset, SEO, internal link and content-safety audit. No network used."""
from pathlib import Path
from html.parser import HTMLParser
import xml.etree.ElementTree as ET
import json,re,sys
root=Path(__file__).resolve().parent.parent
pages=json.loads((root/'data/pages.json').read_text())
basepaths={'/'+(o['path']+'/' if o['path'] else '') for o in pages.values()}
problems=[];titles=set();noindex={'state','telangana','ssc','upsc','defence','teaching','search','job','saved','alerts','dates','qualifications','examupdates','autonotices'}
class Audit(HTMLParser):
 def __init__(self):super().__init__();self.tags=[]
 def handle_starttag(self,tag,attrs):self.tags.append((tag,dict(attrs)))
for key,meta in pages.items():
 folder=root/meta['path']
 file=folder/'index.html'
 if not file.exists():problems.append(f'Missing HTML {file}');continue
 text=file.read_text();parser=Audit();parser.feed(text)
 def tagged(name,attr=None,value=None):return [(tag,a) for tag,a in parser.tags if tag==name and (attr is None or a.get(attr)==value)]
 title=re.search(r'<title>(.*?)</title>',text)
 if not title or title.group(1) in titles:problems.append(f'Duplicate/missing title: {key}')
 if title:titles.add(title.group(1))
 if not tagged('meta','name','description'):problems.append(f'Missing description: {key}')
 if not tagged('link','rel','canonical'):problems.append(f'Missing canonical: {key}')
 if not tagged('meta','property','og:title') or not tagged('meta','name','twitter:card'):problems.append(f'Missing social meta: {key}')
 if not tagged('script','type','application/ld+json'):problems.append(f'Missing JSON-LD: {key}')
 else:
  try:json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',text).group(1))
  except Exception:problems.append(f'Invalid JSON-LD: {key}')
 expected='noindex,follow' if key in noindex else 'index,follow'
 if f'name="robots" content="{expected}"' not in text:problems.append(f'Wrong robots meta: {key}')
 for tag,a in parser.tags:
  for attr in ('src','href'):
   val=a.get(attr,'')
   if not val.startswith('/') or val.startswith('//'):continue
   target=val.split('?')[0].split('#')[0]
   if target.endswith('/'):
    if target not in basepaths:problems.append(f'Unknown route {target} in {key}')
   elif not (root/target.lstrip('/')).is_file():problems.append(f'Missing local asset {target} in {key}')
 if 'bytebright-converter.netlify.app' in text:problems.append('Existing ByteBright site improperly present in generated pages')
# Check page links authored in dynamic JS (all routes except current-relative paths)
app=(root/'assets/js/app.mjs').read_text()
for url in set(re.findall(r"(?<![\w])/(?:[a-z][a-z-]*/)+",app)):
 if url not in basepaths and not url.startswith(('/assets/','/data/')):
  problems.append(f'Unknown dynamic site route: {url}')
ET.parse(root/'sitemap.xml')
sm=(root/'sitemap.xml').read_text()
if '<loc>https://jobpath-india.netlify.app/job/' in sm:problems.append('Demo job pages incorrectly in sitemap')
if len(re.findall('<loc>',sm))!=len(pages)-len(noindex):problems.append('Sitemap entry count mismatch')
if 'Sitemap:' not in (root/'robots.txt').read_text():problems.append('Missing sitemap robots directive')
if 'eval(' in app or 'innerHTML = user' in app:problems.append('Unsafe dynamic JS pattern')
if 'bytebright-converter' in app:problems.append('ByteBright link embedded')
print(f'Audited {len(pages)} page routes, {len(re.findall("<loc>",sm))} indexable sitemap URLs, HTML metadata, JSON-LD, local assets and JS internal routes')
if problems:
 for x in problems:print('FAIL',x)
 sys.exit(1)
print('PASS: no unresolved static links, duplicate titles, missing metadata or accidental demo index entries')
