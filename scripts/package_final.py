#!/usr/bin/env python3
"""Create a minimal single-upload Netlify ZIP and a separate development-only source archive."""
from pathlib import Path
import zipfile,hashlib,os,json
root=Path(__file__).resolve().parent.parent
out=Path('/mnt/data')
prod=out/'JOBPATH_INDIA_V2_1_SINGLE_UPLOAD.zip'
source=out/'JOBPATH_INDIA_V2_1_SOURCE.zip'
pages=json.loads((root/'data/pages.json').read_text())
public_files=[root/'index.html',root/'robots.txt',root/'sitemap.xml',root/'netlify.toml',root/'googlefcd24aba957dc07b.html']
for page in pages.values():
 if page['path']:public_files.append(root/page['path']/'index.html')
for folder in ['assets','data']:
 public_files.extend(x for x in (root/folder).rglob('*') if x.is_file())
public_files=sorted(set(public_files))
for p in public_files:
 if not p.is_file():raise FileNotFoundError(p)
# keep source documents/tests entirely out of the published site
assert not any('/tools/' in str(p) or '/tests/' in str(p) or p.name.startswith('README') for p in public_files)
with zipfile.ZipFile(prod,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for file in public_files:z.write(file,file.relative_to(root).as_posix())
source_files=[p for p in root.rglob('*') if p.is_file() and not any(part in {'__pycache__','.git','node_modules'} for part in p.relative_to(root).parts)]
with zipfile.ZipFile(source,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for file in sorted(source_files):z.write(file,file.relative_to(root).as_posix())
for archive in (prod,source):
 with zipfile.ZipFile(archive) as z:
  assert z.testzip() is None
  names=z.namelist()
  assert len(names)==len(set(names))
  assert 'index.html' in names and 'sitemap.xml' in names and 'googlefcd24aba957dc07b.html' in names
  print(f'{archive.name}: {len(names)} files, {archive.stat().st_size:,} compressed bytes, sha256={hashlib.sha256(archive.read_bytes()).hexdigest()}')
print('Public ZIP excludes local admin / source scripts:',not any(n.startswith(('tools/','scripts/','tests/')) for n in zipfile.ZipFile(prod).namelist()))
