import json, pathlib, html, re
root=pathlib.Path(__file__).resolve().parent.parent
jobs=[
 ('DEMO-001','Sample Graduate Administrative Roles','Example Central Recruitment Office','Central','All India','Any Degree','Administration','SSC','2026-10-30','2026-11-25','2026-10-18'),
 ('DEMO-002','Sample Railway Technical Trainee','Example Rail Recruitment Office','Central','All India','ITI','Technical','Railway','2026-10-27','2026-11-18','2026-10-17'),
 ('DEMO-003','Sample Banking Assistant','Example Banking Careers Unit','Central','All India','Any Degree','Banking','Banking','2026-11-05','2026-12-10','2026-10-15'),
 ('DEMO-004','Sample AP Junior Assistant','Example Andhra Pradesh Department','State','Andhra Pradesh','12th Pass','Administration','State','2026-10-20','2026-10-25','2026-10-05'),
 ('DEMO-005','Sample Telangana Data Assistant','Example Telangana Department','State','Telangana','Diploma','IT','State','2026-11-01','2026-11-28','2026-10-15'),
 ('DEMO-006','Sample Civil Services Training Listing','Example Civil Services Office','Central','All India','Any Degree','Administration','UPSC','2026-11-15','2026-12-20','2026-10-19'),
 ('DEMO-007','Sample Defence Technical Opening','Example Defence Department','Central','All India','B.Tech / Engineering','Defence','Police & Defence','2026-10-29','2026-11-19','2026-10-11'),
 ('DEMO-008','Sample School Teaching Role','Example State Education Unit','State','Andhra Pradesh','Postgraduate','Education','Teaching','2026-10-01','2026-10-15','2026-09-25'),
 ('DEMO-009','Sample SSC Support Role','Example Staff Recruitment Unit','Central','All India','10th Pass','Administration','SSC','2026-10-28','2026-11-16','2026-10-20'),
 ('DEMO-010','Sample Police Technical Support','Example State Police Unit','State','Telangana','B.Tech / Engineering','Police','Police & Defence','2026-11-02','2026-12-05','2026-10-21')]
records=[]
for id,title,org,typ,state,qual,dept,cat,start,last,pub in jobs:
 records.append(dict(id=id,title=title,organization=org,type=typ,state=state,qualification=qual,department=dept,category=cat,minAge=None,maxAge=None,vacancies=None,payScale=None,startDate=start,lastDate=last,publishedDate=pub,fees=None,selectionProcess='Not specified — illustrative entry only',notificationUrl=None,applicationUrl=None,sourceOrganization='Fictional example — no official source',lastVerifiedDate=None,verified=False,isDemo=True,status='unverified',description='This is a fictional example used to demonstrate JobPath India features. No actual vacancy, notification, eligibility, fees or application is represented here.'))
(root/'data/jobs.json').write_text(json.dumps(records,indent=2,ensure_ascii=False)+'\n')
sources=[
 dict(id='upsc',name='Union Public Service Commission (UPSC)',category='Central',url='https://upsc.gov.in/',note='Recruitment notices, examination calendars and official updates.'),
 dict(id='ssc',name='Staff Selection Commission (SSC)',category='Central',url='https://ssc.gov.in/',note='SSC examination and recruitment notices.'),
 dict(id='ibps',name='Institute of Banking Personnel Selection (IBPS)',category='Banking',url='https://www.ibps.in/',note='Common recruitment process information.'),
 dict(id='sbi',name='State Bank of India Careers',category='Banking',url='https://sbi.co.in/web/careers',note='SBI careers and announcements.'),
 dict(id='rrb',name='Railway Recruitment Board Chandigarh',category='Railway',url='https://www.rrbcdg.gov.in/',note='One RRB information portal. Select your relevant RRB region.'),
 dict(id='appsc',name='Andhra Pradesh Public Service Commission',category='State',url='https://psc.ap.gov.in/',note='Andhra Pradesh commission website.'),
 dict(id='tgpsc',name='Telangana Public Service Commission',category='State',url=None,note='Check the current official Telangana commission domain from an authoritative state government directory before use.'),
 dict(id='ctet',name='Central Teacher Eligibility Test',category='Teaching',url='https://ctet.nic.in/',note='Eligibility test website; not a live vacancy listing.'),
 dict(id='army',name='Join Indian Army',category='Defence',url='https://joinindianarmy.nic.in/',note='Army recruitment information; confirm all notices directly.'),
]
(root/'data/sources.json').write_text(json.dumps(sources,indent=2)+'\n')
pages={
 'home':('','Government Jobs Information, Exams & Official Sources','Independent Indian government recruitment information portal. Explore official recruitment sources, sample search tools, exam guides, and state-wise navigation.'),
 'latest':('latest-jobs','Latest Government Jobs','Recruitment browsing interface with clearly labeled demonstration records. No live verified vacancy notifications are published yet.'),
 'central':('central-government-jobs','Central Government Jobs','Explore central government recruitment routes, exam bodies, and sample filters. Confirm all current notifications on official sites.'),
 'state':('state-government-jobs','State Government Jobs','Find state-specific government recruitment sources and try the location filters with demo data.'),
 'ap':('andhra-pradesh-jobs','Andhra Pradesh Government Jobs','Find Andhra Pradesh recruitment information and links to commission sources. Only fictional examples are shown until verification.'),
 'telangana':('telangana-jobs','Telangana Government Jobs','Explore Telangana recruitment categories and demonstration search tools. Check current notices directly with the commission.'),
 'railway':('railway-jobs','Railway Recruitment','Explore Railway Recruitment Board resources and sample railway search results.'),
 'banking':('banking-jobs','Banking Government Jobs','Find banking recruitment authorities and learn how to verify bank career announcements.'),
 'ssc':('ssc-recruitment','SSC Recruitment','Staff Selection Commission recruitment information and source directory.'),
 'upsc':('upsc-recruitment','UPSC Recruitment','Union Public Service Commission recruitment and examination information.'),
 'defence':('police-defence-jobs','Police & Defence Jobs','Find defence and police recruitment sources; confirm official notices before applying.'),
 'teaching':('teaching-jobs','Teaching Jobs','Teaching eligibility and recruitment information with example filtering.'),
 'qualifications':('qualification-wise-jobs','Jobs by Qualification','Find 10th, 12th, ITI, Diploma, degree, engineering, and postgraduate pathways.'),
 'admit':('admit-cards','Government Exam Admit Cards','A guide to safely obtaining admit cards from official examination portals.'),
 'results':('exam-results','Government Exam Results','A guide to checking official examination results and protecting your details.'),
 'syllabus':('exam-syllabus','Government Exam Syllabus','Find official examination syllabus information and preparation guidance.'),
 'upcoming':('upcoming-exams','Upcoming Government Exams','How to track examination calendars and official announcements.'),
 'dates':('important-dates','Important Application Dates','Demo deadline tracker and guidance for verifying application windows.'),
 'job':('job','Job Details','Illustrative recruitment detail view for testing portal functionality.'),
 'search':('job-search','Search and Filter Jobs','Filter illustrative government jobs by state, qualification, category, and application dates.'),
 'saved':('saved-jobs','Saved Jobs','View jobs saved locally in this browser.'),
 'alerts':('job-alerts','Job Alerts & Preferences','Local-only saved job preferences and explanation of future alert features.'),
 'sources':('official-sources','Official Recruitment Source Directory','Links and guidance for finding authentic government recruitment notices.'),
 'about':('about','About JobPath India','About this independent Indian government jobs information project.'),
 'contact':('contact','Contact JobPath India','Contact and correction information for JobPath India.'),
 'privacy':('privacy-policy','Privacy Policy','How JobPath India uses local browser storage and protects privacy.'),
 'terms':('terms','Terms and Conditions','Terms of use for the independent JobPath India website.'),
 'disclaimer':('disclaimer','Disclaimer','Important independence, non-affiliation and recruitment verification information.'),
}
(root/'data/pages.json').write_text(json.dumps({k:dict(path=v[0],title=v[1],description=v[2]) for k,v in pages.items()},indent=2)+'\n')
# Canonical initially relative; configure-domain.mjs rewrites to final absolute URLs after deployment hostname chosen.
noindex_pages={'latest','central','state','ap','telangana','railway','banking','ssc','upsc','defence','teaching','search','job','saved','alerts','dates','qualifications'}
for key,(path,title,description) in pages.items():
 urlpath='/'+(path+'/' if path else '')
 rel='../' if path else ''
 htmlpage=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#102e5f"><title>{html.escape(title)} | JobPath India</title><meta name="description" content="{html.escape(description,quote=True)}"><meta name="robots" content="{'noindex,follow' if key in noindex_pages else 'index,follow'}"><link rel="canonical" href="{urlpath}"><meta property="og:type" content="website"><meta property="og:site_name" content="JobPath India"><meta property="og:title" content="{html.escape(title,quote=True)} | JobPath India"><meta property="og:description" content="{html.escape(description,quote=True)}"><meta property="og:url" content="{urlpath}"><meta name="twitter:card" content="summary"><meta name="twitter:title" content="{html.escape(title,quote=True)} | JobPath India"><meta name="twitter:description" content="{html.escape(description,quote=True)}"><link rel="icon" type="image/svg+xml" href="/assets/icons/favicon.svg"><link rel="stylesheet" href="/assets/css/styles.css"><script type="module" src="/assets/js/app.mjs"></script></head><body data-page="{key}"><a class="skip" href="#main">Skip to main content</a><div id="app"><main id="main"><div class="wrap"><h1>{html.escape(title)}</h1><p>Loading...</p></div></main></div></body></html>
'''
 dest=(root/path/'index.html') if path else root/'index.html';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(htmlpage)
# sitemap URLs are provisional until actual Netlify site name is known.
from xml.sax.saxutils import escape
urls=['/'+(p+'/' if p else '') for k,(p,_,_) in pages.items() if k not in noindex_pages]
(root/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'  <url><loc>{escape("https://jobpath-india.netlify.app"+path)}</loc></url>\n' for path in urls)+'</urlset>\n')
(root/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: https://jobpath-india.netlify.app/sitemap.xml\n')
(root/'netlify.toml').write_text('''[build]
  publish = "."
[[headers]]
  for = "/*"
  [headers.values]
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
    X-Frame-Options = "DENY"
    Permissions-Policy = "camera=(), microphone=(), geolocation=()"
[[headers]]
  for = "/assets/*"
  [headers.values]
    Cache-Control = "public, max-age=86400"
''')
print('Generated',len(pages),'pages,',len(jobs),'demo records and',len(sources),'sources')
