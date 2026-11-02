#!/usr/bin/env node
/** A source-first editorial quality pulse. It reports, but cannot verify a live notice. */
import fs from 'node:fs';
const jobs=JSON.parse(fs.readFileSync(new URL('../data/jobs.json',import.meta.url),'utf8'));
const today=new Date().toISOString().slice(0,10);
const day=(d)=>Number.isFinite(Date.parse(d+'T00:00:00Z'))?Math.round((Date.parse(d+'T00:00:00Z')-Date.parse(today+'T00:00:00Z'))/86400000):null;
const genuine=jobs.filter(j=>j.verified===true&&j.isDemo!==true);
const current=genuine.filter(j=>j.status==='open'&&day(j.lastDate)!==null&&day(j.lastDate)>=0);
const soon=current.filter(j=>day(j.lastDate)<=7);
const expiredOpen=genuine.filter(j=>j.status==='open'&&day(j.lastDate)!==null&&day(j.lastDate)<0);
const awaitingReview=genuine.filter(j=>!j.lastVerifiedDate||day(j.lastVerifiedDate)!==null&&day(j.lastVerifiedDate)<-14);
const demos=jobs.filter(j=>j.isDemo===true);
const warning=[];
if(expiredOpen.length)warning.push(expiredOpen.length+' records still have source status=open despite elapsed deadlines. Browser/static logic must not present these as current.');
if(awaitingReview.length)warning.push(awaitingReview.length+' records were last checked over 14 days ago or lack a check date.');
if(!current.length)warning.push('No future-dated open verified records; public listings may be intentionally empty.');
const rows=[
'# JobPath India — source-first editorial pulse','',
'Generated: '+new Date().toISOString(),'',
'| Metric | Count |','| --- | ---: |',
'| Stored records | '+jobs.length+' |',
'| Source-reviewed non-demo records | '+genuine.length+' |',
'| Open with application deadline not elapsed | '+current.length+' |',
'| Application deadlines within 7 days | '+soon.length+' |',
'| Records labeled open but deadline elapsed | '+expiredOpen.length+' |',
'| Reviewed records older than 14 days | '+awaitingReview.length+' |',
'| Demo-only records (must stay excluded from public results) | '+demos.length+' |',
'',
'## Deadlines approaching (not live confirmations)',
...(soon.length?soon.sort((a,b)=>a.lastDate.localeCompare(b.lastDate)).slice(0,15).map(j=>'- '+String(j.organization+' — '+j.title).replace(/[\r\n|]/g,' ').slice(0,155)+' · '+j.lastDate):['- None in source records']),
'',
'## Editorial actions',
...(warning.length?warning.map(x=>'- REVIEW: '+x):['- No deadline/verification-age warnings from stored data.']),
'',
'This report uses repository dates only. Official recruitment notices, extensions and current link availability must be independently verified.',
''
];
const report=rows.join('\n');
console.log(report);
if(process.env.GITHUB_STEP_SUMMARY)fs.appendFileSync(process.env.GITHUB_STEP_SUMMARY,report+'\n');
