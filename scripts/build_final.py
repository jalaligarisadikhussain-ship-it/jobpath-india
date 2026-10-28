#!/usr/bin/env python3
"""Build independent JobPath India static pages from editorial data with resilient HTML fallback."""
from pathlib import Path
import json,html,datetime,re
from xml.sax.saxutils import escape as xml_escape
root=Path(__file__).resolve().parent.parent
base='https://jobpath-india.netlify.app'
pages=json.loads((root/'data/pages.json').read_text())
source=json.loads((root/'data/sources.json').read_text())
regions=json.loads((root/'data/regions.json').read_text())
exams=json.loads((root/'data/exam-updates.json').read_text())
jsdata={p:json.loads((root/p.lstrip('/')).read_text()) for p in ['/data/jobs.json','/data/sources.json','/data/pages.json','/data/exam-updates.json','/data/regions.json','/data/notice-watch.json','/data/auto-notices.json']}
inline_json=json.dumps(jsdata,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
noindex={'state','telangana','ssc','upsc','defence','teaching','search','job','saved','alerts','dates','qualifications','examupdates','autonotices'}
nav=[('Home','/'),('Latest Jobs','/latest-jobs/'),('Auto Notices','/auto-recruitment-notices/'),('All States','/states-directory/'),('SSC','/ssc-recruitment/'),('UPSC','/upsc-recruitment/'),('Exam Calendar','/exam-calendar/'),('Exam Updates','/exam-updates/'),('Official Sources','/official-sources/'),('Notice Desk','/recruitment-updates/')]
seo_text={
'home':('Government Jobs Research Across India','Find the issuing authority before you apply. Navigate recruitment boards, region-specific information, exam guides, source verification and qualification categories. The portal only displays source-checked vacancies publicly.'),
'latest':('Latest Government Jobs: Verification First','Browse the official-source-checked job database and always open the issuing authority recruitment notice before applying.'),
'central':('Central Government Recruitment Information','Compare SSC, UPSC, railway, banking and other recruiting organizations. Each examination cycle has its own eligibility, notice number and application instructions.'),
'state':('State Government Recruitment Information','Recruitment notices may be issued by state public service commissions, police boards, education departments or other departments; always check the real issuer.'),
'ap':('Andhra Pradesh Government Recruitment Research','For APPSC, teaching and departmental vacancies, consult the relevant issuing body and verify official recruitment notifications before acting.'),
'telangana':('Telangana Government Recruitment Research','For TGPSC, Telangana education, police and departmental recruitments, cross-check the current commission website and official notices.'),
'railway':('Railway Recruitment Board Information','Different Railway Recruitment Boards handle regional recruitment. Verify board selection, CEN or advertisement number, eligibility and corrections.'),
'banking':('Banking Recruitment and Career Notices','Read IBPS, SBI and bank-specific career notices from issuer websites and distinguish recruitment from examination calendar announcements.'),
'ssc':('SSC Recruitment and Examination Updates','Find SSC recruitment-source guidance and the October 2026 exam date notice confirmed on SSC notice board; date table still pending original PDF review.'),
'upsc':('UPSC Recruitment and Civil Services Information','Use the relevant UPSC exam notification, eligibility rules and latest examination calendar rather than a generalized vacancy listing.'),
'defence':('Police and Defence Recruitment Guidance','Army, Navy, Air Force and police roles use different recruitment portals and specific physical, educational, medical and age criteria.'),
'teaching':('Teaching Recruitment and Eligibility Tests','Eligibility examinations such as CTET differ from advertised teaching vacancies. Check employer notices, required qualifications and documents.'),
'qualifications':('Qualification-wise Government Job Search','Explore 10th, 12th, ITI, diploma, degree, B.Tech, postgraduate and other categories. Eligibility depends on the real advertisement.'),
'admit':('Government Exam Admit Cards','An admit card should be downloaded from the official authority candidate portal. Check your exam center, reporting time, name and required identification.'),
'results':('Government Exam Results','Check examination year, result notice, merit-list status and document verification instructions on the original publisher website.'),
'syllabus':('Government Exam Syllabus','Match the official syllabus, exam scheme, year and notice number. Coaching-site PDFs may not reflect the latest changes.'),
'upcoming':('Upcoming Government Examination Planning','Exam timetables may change through corrigenda. Track application windows, exam dates, city intimation, admit cards and results separately.'),
'dates':('Application Deadline Research','Current application deadlines were source checked on 28 October 2026. Verify the original notice and extension amendments with the recruiting body.'),
'job':('Job Details and Recruitment Source Verification','Real job records link to the original notice and official application portal; demonstration records are clearly labeled.'),
'search':('Advanced Job Search','Filter verified vacancies by organization, state, qualification, status and deadline. Training examples are shown only with an explicit demo setting.'),
'saved':('Saved Job Bookmarks','Saved references are browser-local. This version does not provide a user account or automatic email/push notifications.'),
'alerts':('Job Alerts: Current Capabilities','Browser-local bookmarks work; email, push and SMS alerts are not currently implemented.'),
'sources':('Official Recruitment Source Directory','Use references to SSC, UPSC, IBPS, railway, state, teaching and defence organizations. Selected issuer references were checked on 28 October 2026; recheck URLs before applying.'),
'about':('About This Independent Portal','JobPath India is a separate independent informational project, not a government website and not an application-processing service.'),
'contact':('Corrections and Contact Information','A public contact inbox has not been configured, so this static site avoids an unusable contact form or invented email address.'),
'privacy':('Privacy and Local Storage','Theme and saved job IDs are stored locally by your browser. The website currently has no active advertising tags or account database.'),
'terms':('Terms and Conditions','Check official recruitment notices before applying or paying official fees. Information provided by this website is not hiring advice.'),
'disclaimer':('No Government Affiliation','JobPath India is an independent informational service. It is not an official Government of India or state recruitment website.'),
'examupdates':('SSC 2026 Revised Proposed Exam Dates','Reader-supplied SSC corrigendum dated 26 October 2026: Junior Engineer Paper I and Sub-Inspector in Delhi Police/CAPFs. Date notice listed on official SSC board; the complete official PDF still awaits comparison.'),
'statesdir':('All 28 States and 8 Union Territories','Browse all Indian states and union territories. A location link does not indicate current vacancies or verified application deadlines.'),
'calendar':('Exam Calendar and Planning Checklist','Keep recruitment, application deadlines, tentative exam dates, admit cards and results separate and recheck corrections.'),
'applicationguide':('How to Apply Safely','Find the issuing organization; match the PDF notice; confirm dates, qualifications and payments; use the true official application portal.'),
'editorial':('How JobPath Verifies Recruitment Information','Review source links, advertisement numbers, dates and corrigenda before posting a real opening; correct or close expired records.'),
'faq':('Frequently Asked Government Job Questions','Answers about official source links, eligibility, sample records, corrections and indexing.'),
'careerguides':('Central, State, Railway and Banking Career Routes','Overview of recruitment organizations and how to verify each career pathway.'),
'autonotices':('Automatically Detected Recruitment Notice Links','Official recruitment notice links detected by a daily automated checker. These are unverified leads, not confirmed open government jobs.'),
'updates':('Source-labeled Exam and Recruitment Notices','An exam-date corrigendum is not a new vacancy. We label reader-submitted documents awaiting independent verification.'),
'maintenance':('Editorial Maintenance Plan','A 30-day source-first content schedule for accuracy, regional coverage, accessibility and search performance.'),
'contactsources':('Official Notice Verification Checklist','Verify issuer, PDF advertisement number, date, eligibility, official links and later amendments.'),
}

def fallback_content(key):
 title,desc=seo_text[key]
 buf=[f'<h1>{html.escape(title)}</h1><p class="lead">{html.escape(desc)}</p>']
 if key=='examupdates':
  buf+=['''<section><h2>SSC revised proposed dates — not final</h2><div class="exam-schedule"><article class="exam-schedule-card"><h3>Junior Engineer Examination, 2026</h3><p>Paper-I (CBE)</p><ul class="exam-windows"><li><strong>Window 1:</strong> <time datetime="2026-11-02">2 November 2026</time> – <time datetime="2026-11-06">6 November 2026</time></li><li><strong>Window 2:</strong> <time datetime="2026-11-30">30 November 2026</time> – <time datetime="2026-12-01">1 December 2026</time></li></ul></article><article class="exam-schedule-card"><h3>Sub-Inspector in Delhi Police and CAPFs Examination, 2026</h3><p>Computer-based examination (CBE)</p><ul class="exam-windows"><li><time datetime="2026-11-23">23 November 2026</time> – <time datetime="2026-11-28">28 November 2026</time></li></ul></article></div><p>Dates are only <strong>revised proposed</strong>. Source: reader-supplied SSC corrigendum screenshots dated 26 October 2026. SSC notice board confirms title/date; full original PDF comparison pending. <a href="https://ssc.gov.in/">Check SSC's latest notices</a>.</p></section>''']
 if key in ('home','latest','central','railway','banking','dates','ap','updates'):
  verified=[j for j in jsdata['/data/jobs.json'] if j.get('verified') and not j.get('isDemo')]
  pick=verified if key in ('home','latest','central','dates') else [j for j in verified if (j.get('category')=='Railway' if key=='railway' else j.get('category')=='Banking' if key=='banking' else False)]
  if pick:
   buf+=['<section><h2>Recruitment notices checked on 28 October 2026</h2><p>These summaries are independent; confirm updated rules and deadlines with the issuing employer.</p><div class="grid">']
   for j in pick[:12]:
    buf.append('<article class="source-card"><h3>'+html.escape(j['title'])+'</h3><p>'+html.escape(j['organization'])+' · '+str(j.get('vacancies') or 'Not specified')+' vacancies · Last application date: '+html.escape(j.get('lastDate') or 'Not verified')+'</p><a href="'+html.escape(j['notificationUrl'],quote=True)+'">Official notice/source →</a></article>')
   buf+=['</div></section>']
  if key in ('home','ap','updates'):
   buf+=['<section><h2>APPSC 2026 notice register</h2><p>APPSC published Group-I (07/2026), Group-II (37/2026), Forest Beat Officer (18/2026) and other notices in October 2026. Exact application dates and qualifications are not verified here. <a href="https://portal-psc.ap.gov.in/HomePages/RecruitmentNotifications">View official APPSC notifications</a>.</p></section>']
 if key in ('home','latest','autonotices','updates'):
  auto_items=jsdata['/data/auto-notices.json'].get('notices',[])
  buf+=['<section class="section"><h2>Automatically detected official recruitment notice links</h2><p><strong>Unverified and not confirmed open vacancies.</strong> Application dates, eligibility and vacancy counts are not established by automatic link detection. Read each original official notice and all corrigenda before applying.</p>']
  if auto_items:
   buf+=['<div class="grid">']
   for n in auto_items[:(40 if key=='autonotices' else 6)]:
    buf.append('<article class="source-card"><p class="tag demo">AUTO-DETECTED · UNVERIFIED</p><h3>'+html.escape(str(n['title']))+'</h3><p>'+html.escape(str(n['organization']))+' · Detected '+html.escape(str(n['detectedDate']))+'</p><a href="'+html.escape(str(n['noticeUrl']),quote=True)+'" rel="noopener noreferrer">Original official notice ↗</a></article>')
   buf+=['</div>']
  else:
   buf+=['<p>No new qualifying source links detected yet. The official sites may not be accessible to the checker.</p>']
  buf+=['</section>']
 if key=='statesdir':
  buf+=['<h2>Indian states</h2><div class="region-grid">'+''.join(f'<a class="region" href="/job-search/?state={html.escape(n)}">{html.escape(n)} →</a>' for n in regions['states'])+'</div><h2>Union territories</h2><div class="region-grid">'+''.join(f'<a class="region" href="/job-search/?state={html.escape(n)}">{html.escape(n)} →</a>' for n in regions['unionTerritories'])+'</div>']
 if key=='sources':
  buf+=['<h2>Known organization website references</h2><div class="grid">'+''.join(f'<article class="panel"><h3>{html.escape(r["name"])}</h3><p>{html.escape(r["note"])}</p>'+(f'<a href="{html.escape(r["url"],quote=True)}">Organization website ↗</a>' if r.get('url') else 'Current official URL not confirmed')+'</article>' for r in source)+'</div>']
 if key in {'careerguides','applicationguide','editorial','contactsources','maintenance','faq'}:
  topics={'careerguides':['Central & state bodies','Railway & banking','Teaching & defence'], 'applicationguide':['Find issuer','Read advertisement','Check eligibility','Confirm official application portal','Save receipt'], 'editorial':['Verify source and last checked date','Keep a correction history','Automatically close expired dates','Separate ads and application links'], 'contactsources':['Notice number and issuer','Dates and eligibility','Corrigenda','Official fee portal'], 'maintenance':['Source review','Recruitment notice quality checks','Regional coverage','Accessibility review','Search performance'], 'faq':['Is this official? No.','Does the site collect fees? No.','Are live openings verified? Not yet.']}
  buf+=['<h2>What this guide covers</h2><ul>'+''.join(f'<li>{html.escape(v)}</li>' for v in topics[key])+'</ul>']
 if key in {'home','latest','search','ap','telangana','state','ssc','railway','banking','upsc'}:
  buf+=['<p><a class="btn btn-primary" href="/official-sources/">Browse recruitment source directory</a> <a class="btn btn-secondary" href="/application-guide/">Application safety checklist</a></p>']
 buf+=['<p><a href="/">Home</a> · <a href="/states-directory/">All states</a> · <a href="/exam-calendar/">Exam calendar</a> · <a href="/editorial-policy/">Editorial policy</a></p>']
 return '\n'.join(buf)

# Keep the search engine and browser fallback independently useful even if JS is blocked.
for key,info in pages.items():
 urlpath='/'+(info['path']+'/' if info['path'] else '')
 url=base+urlpath
 title=html.escape(info['title']+' | JobPath India')
 desc=html.escape(info['description'],quote=True)
 meta_status='noindex,follow' if key in noindex else 'index,follow'
 breadcrumb=[{'@type':'ListItem','position':1,'name':'Home','item':base+'/'}]
 if key!='home':breadcrumb.append({'@type':'ListItem','position':2,'name':info['title'],'item':url})
 schema={'@context':'https://schema.org','@graph':[{'@type':'WebSite','name':'JobPath India','url':base+'/','inLanguage':'en-IN','description':'Independent non-government recruitment research website.'},{'@type':'WebPage','name':info['title'],'url':url,'description':info['description'],'inLanguage':'en-IN','isPartOf':{'@id':base+'/'},'breadcrumb':{'@type':'BreadcrumbList','itemListElement':breadcrumb}}]}
 static_nav=' '.join(f'<a href="{p}">{html.escape(t)}</a>' for t,p in nav)
 text=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#102e5f"><title>{title}</title><meta name="description" content="{desc}"><meta name="robots" content="{meta_status}"><link rel="canonical" href="{html.escape(url,quote=True)}"><meta property="og:type" content="website"><meta property="og:site_name" content="JobPath India"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:url" content="{html.escape(url,quote=True)}"><meta name="twitter:card" content="summary"><meta name="twitter:title" content="{title}"><meta name="twitter:description" content="{desc}"><link rel="icon" type="image/svg+xml" href="/assets/icons/favicon.svg"><link rel="stylesheet" href="/assets/css/styles.css?v=release-3-0"><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False,separators=(',',':'))}</script><script id="jobpath-data" type="application/json">{inline_json}</script><script type="module" src="/assets/js/app.mjs?v=release-3-0"></script></head><body data-page="{key}"><a class="skip" href="#main">Skip to main content</a><div id="app"><header class="site-header"><div class="wrap"><nav aria-label="Navigation" class="nav-wrap">{static_nav}</nav></div></header><div class="info-banner"><div class="wrap"><strong>Independent information website.</strong> Not affiliated with any government agency. Refer to official source notices and check last verification dates.</div></div><main id="main"><div class="wrap"><section class="page-intro">{fallback_content(key)}</section></div></main><footer class="footer"><div class="wrap">JobPath India · Independent recruitment information · <a href="/disclaimer/">Disclaimer</a></div></footer></div></body></html>
'''
 target=root/info['path']/'index.html';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text)
urls=[base+'/'+(v['path']+'/' if v['path'] else '') for k,v in pages.items() if k not in noindex]
sitemap='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'  <url><loc>{xml_escape(url)}</loc></url>\n' for url in urls)+'</urlset>\n'
(root/'sitemap.xml').write_text(sitemap)
(root/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: https://jobpath-india.netlify.app/sitemap.xml\n')
(root/'netlify.toml').write_text('''[build]
  command = "python3 scripts/build_dist.py"
  publish = "dist"
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
    Cache-Control = "public, max-age=600, must-revalidate"
[[headers]]
  for = "/data/*"
  [headers.values]
    Cache-Control = "public, max-age=300, must-revalidate"
''')
print(f'Built {len(pages)} HTML routes, {len(urls)} sitemap URLs, {len(source)} organization references; embedded JSON for offline resilience.')
