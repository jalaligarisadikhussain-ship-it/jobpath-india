from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
root=Path(__file__).resolve().parent.parent
out=root.parent
prod=out/'JOBPATH_INDIA_V1_NETLIFY.zip'
source=out/'JOBPATH_INDIA_V1_SOURCE.zip'
excludes={'.gitignore'}
static={'index.html','robots.txt','sitemap.xml','netlify.toml'}
for archive,full in ((prod,False),(source,True)):
 with ZipFile(archive,'w',compression=ZIP_DEFLATED,compresslevel=9) as z:
  for f in sorted(root.rglob('*')):
   if not f.is_file() or '__pycache__' in f.parts or f.name.endswith('.pyc'):continue
   rel=f.relative_to(root).as_posix()
   if not full and not (rel in static or rel.startswith(('assets/','data/')) or rel.endswith('/index.html')):continue
   arc=('jobpath-india/'+rel) if full else rel
   z.write(f,arc)
 print(archive,archive.stat().st_size,'bytes')
