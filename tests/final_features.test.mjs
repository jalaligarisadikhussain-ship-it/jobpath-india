import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
const root=new URL('../',import.meta.url);
const read=name=>fs.readFileSync(new URL(name,root),'utf8');
const pages=JSON.parse(read('data/pages.json'));
const regions=JSON.parse(read('data/regions.json'));
const sources=JSON.parse(read('data/sources.json'));
test('complete country region directory lists exactly 28 states and 8 union territories',()=>{
 assert.equal(regions.states.length,28);assert.equal(regions.unionTerritories.length,8);
 assert.equal(new Set([...regions.states,...regions.unionTerritories]).size,36);
 assert(regions.states.includes('Andhra Pradesh')&&regions.states.includes('Telangana'));
});
test('no secret keys, injected advertisements, ByteBright links or invented verified jobs in public data',()=>{
 const js=read('assets/js/app.mjs'), jobs=JSON.parse(read('data/jobs.json'));
 assert(jobs.filter(j=>j.verified).length>=10);assert(jobs.filter(j=>j.isDemo).every(j=>j.verified===false));
 assert(!js.toLowerCase().includes('bytebright-converter.netlify.app'));
 assert(!read('index.html').includes('bytebright-converter.netlify.app'));
 const adSettings=JSON.parse(read('data/ads-config.json'));
 if(!adSettings.enabled){
  assert(!read('index.html').includes('adsbygoogle'));
 }else{
  assert.match(read('index.html'),/pagead2\\.googlesyndication\\.com/);
 }
 assert(!read('index.html').includes('gtag('));
});
test('every page has safe self-contained embedded JSON and metadata',()=>{
 for(const page of Object.values(pages)){
  const f=page.path?page.path+'/index.html':'index.html';const html=read(f);
  assert.match(html,/<script id="jobpath-data" type="application\/json">/);
  const match=html.match(/<script id="jobpath-data" type="application\/json">([\s\S]*?)<\/script>/);
  const j=JSON.parse(match[1]);assert.equal(j['/data/regions.json'].states.length,28);
  assert(html.includes('rel="canonical"')&&html.includes('name="robots"')&&html.includes('application/ld+json'));
  assert(!html.includes('<title>Loading</title>'));
 }
 assert(Object.keys(pages).length>=39);assert(pages.autonotices);
});
test('automatic recruitment notices are publicly available but not verified jobs',()=>{
 const page=read('auto-recruitment-notices/index.html');
 const feed=JSON.parse(read('data/auto-notices.json'));
 assert.match(page,/AUTO|Automatically/i);
 assert.match(page,/noindex,follow/);
 assert(!read('sitemap.xml').includes('/auto-recruitment-notices/'));
 assert(Array.isArray(feed.notices));
 for(const item of feed.notices){
  assert.equal(item.verificationStatus,'automatically_detected_unverified');
  assert.equal(item.applicationStatus,'unknown');
  assert(!('vacancies' in item));
  assert(!('lastDate' in item));
  assert(!('applicationUrl' in item));
 }
});
test('unverified SSC notice stays noindex and excluded from sitemap',()=>{
 assert.match(read('exam-updates/index.html'),/name="robots" content="noindex,follow"/);
 assert.doesNotMatch(read('sitemap.xml'),/\/exam-updates\//);
 assert.match(read('exam-updates/index.html'),/datetime="2026-11-30"/);
 assert.match(read('exam-updates/index.html'),/datetime="2026-12-01"/);
 assert.match(read('exam-updates/index.html'),/class="exam-schedule"/);
});
test('directory has categorized organizations and no invented URLs for unknown commission',()=>{
 assert(sources.length>=19);
 assert(sources.some(s=>s.id==='ssc'&&s.url==='https://ssc.gov.in/'));
 assert(sources.some(s=>s.id==='tgpsc'&&s.url==='https://www.tgpsc.gov.in/'));
 assert(sources.every(s=>!s.url||new URL(s.url).protocol==='https:'));
});

test('exam date cards are vertical-friendly and data retains proposed status',()=>{
 const js=read('assets/js/app.mjs'),css=read('assets/css/styles.css');
 const notice=JSON.parse(read('data/exam-updates.json'))[0];
 assert.match(js,/exam-schedule-card/);
 assert.match(js,/PROPOSED · NOT FINAL/);
 assert.match(js,/<time datetime=/);
 assert.match(css,/@media\(max-width:740px\)/);
 assert.match(css,/\.exam-schedule\{grid-template-columns:minmax\(0,1fr\)\}/);
 assert.match(css,/prefers-reduced-motion/);
 assert.equal(notice.revisedProposedExams[0].windows.length,2);
 assert.equal(notice.directOfficialNoticeUrl,null);
});

test('mobile toast and responsive menu improvements remain accessible',()=>{
 const js=read('assets/js/app.mjs'),css=read('assets/css/styles.css');
 assert.match(js,/ev.key==='Escape'/);
 assert.match(js,/aria-expanded/);
 assert.match(js,/className='app-toast'/);
 assert.match(css,/\.footer\{padding-bottom:105px\}/);
 assert.doesNotMatch(css,/\.detail-table\{min-width:470px\}/);
});
