import subprocess, time, os, sys, socket, json, traceback, urllib.parse, mimetypes
from playwright.sync_api import sync_playwright
ROOT=os.path.dirname(os.path.dirname(__file__))
port=18888
server=None
checks=[]
def check(name,condition):
    checks.append((name,bool(condition)))
    if not condition:print('FAIL',name)
    else: print('PASS',name)
try:
 time.sleep(0.7)
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  page=browser.new_page(viewport={'width':1360,'height':900})
  errors=[]
  page.on('pageerror',lambda exc:errors.append(str(exc)))
  base='http://127.0.0.1:18888'
  def fake_routes(route):
   path=urllib.parse.urlparse(route.request.url).path.lstrip('/')
   local=os.path.join(ROOT,path)
   if os.path.isdir(local):local=os.path.join(local,'index.html')
   if not os.path.commonpath([ROOT,os.path.abspath(local)])==ROOT or not os.path.isfile(local):
    route.fulfill(status=404,body='Not Found');return
   ctype=mimetypes.guess_type(local)[0] or 'application/octet-stream'
   route.fulfill(status=200,content_type=ctype,body=open(local,'rb').read())
  page.route('**/*',fake_routes)
  page.goto(base+'/',wait_until='networkidle')
  check('Homepage hero renders',page.get_by_role('heading',name='Explore opportunities with a clearer path.').count()==1)
  check('Homepage 12 navigation tiles',page.locator('.tile').count()>=12)
  check('No unverified cards on homepage',page.locator('.job-card').count()==0)
  check('Source directory visible',page.get_by_text('Official Recruitment Source Directory').count()==0 and page.get_by_text('Start with the official source').count()==1)
  page.goto(base+'/job-search/',wait_until='networkidle')
  check('Public job search contains zero unverified cards',page.locator('.job-card').count()==0)
  check('Clear no verified notices notice shown',page.get_by_text('No independently verified vacancy records yet').count()==1)
  page.goto(base+'/job-search/?demo=1',wait_until='networkidle')
  check('Training mode contains 10 clearly fictional records',page.locator('.job-card').count()==10 and page.get_by_text('TRAINING MODE').count()>=1)
  page.locator('#filter-q').fill('Railway')
  page.wait_for_timeout(280)
  check('Keyword search filters',page.locator('.job-card').count()==1)
  page.locator('#filter-q').fill('')
  page.wait_for_timeout(260)
  page.select_option('#filter-state','Telangana')
  check('State filter',page.locator('.job-card').count()==2)
  page.select_option('#filter-qualification','Diploma')
  check('Combined filters',page.locator('.job-card').count()==1)
  page.get_by_role('button',name='Clear filters').click()
  check('Clear filters',page.locator('.job-card').count()==10)
  page.get_by_role('button',name='♡ Save',exact=False).first.click()
  page.goto(base+'/saved-jobs/',wait_until='networkidle')
  check('Bookmark persisted',page.locator('.job-card').count()==1)
  page.reload(wait_until='networkidle')
  check('Bookmark persisted across reload',page.locator('.job-card').count()==1)
  page.locator('[data-theme-toggle]').click()
  check('Dark mode active',page.locator('html').get_attribute('data-theme')=='dark')
  page.reload(wait_until='networkidle')
  check('Dark mode persisted',page.locator('html').get_attribute('data-theme')=='dark')
  page.goto(base+'/job/?id=DEMO-001',wait_until='networkidle')
  check('Job detail renders',page.get_by_role('heading',name='Sample Graduate Administrative Roles').count()==1)
  check('Job detail no fake application',page.get_by_text('NOT A REAL GOVERNMENT JOB.').count()==1)
  page.goto(base+'/official-sources/',wait_until='networkidle')
  check('Source directory has entries',page.locator('.source-card').count()==9)
  check('HTTPS sources rendered',page.locator('.source-card a[href^="https://"]').count()>=6)
  # Check all pages render without server errors (28 routes)
  paths=list(json.load(open(ROOT+'/data/pages.json')).values())
  failed=[]
  for obj in paths:
   r=page.goto(base+'/'+(obj['path']+'/' if obj['path'] else ''),wait_until='domcontentloaded')
   page.locator('.site-header').wait_for(timeout=5000)
   if r.status!=200 or page.locator('main h1').count()!=1:failed.append((obj['path'],r.status))
  check('All 28 HTML pages respond and render',len(failed)==0)
  check('No JavaScript page exceptions',len(errors)==0)
  # Mobile test
  m=browser.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
  m.route('**/*',fake_routes)
  m.goto(base+'/',wait_until='networkidle')
  check('Mobile menu button available',m.locator('[data-menu]').is_visible())
  m.locator('[data-menu]').click()
  check('Mobile navigation expands',m.locator('#primary-nav').is_visible())
  check('Mobile page no horizontal overflow',m.evaluate('document.documentElement.scrollWidth <= window.innerWidth+1'))
  m.goto(base+'/job-search/',wait_until='networkidle')
  check('Mobile search input usable',m.locator('#filter-q').is_visible())
  check('Mobile search no horizontal overflow',m.evaluate('document.documentElement.scrollWidth <= window.innerWidth+1'))
  browser.close()
finally:
 pass
print(f'\nBrowser checks: {sum(v for _,v in checks)}/{len(checks)} passed')
if any(not v for _,v in checks):sys.exit(1)
