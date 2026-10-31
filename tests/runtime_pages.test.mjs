import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {pathToFileURL} from 'node:url';
import path from 'node:path';
const root=path.resolve(new URL('..',import.meta.url).pathname);
const pages=JSON.parse(fs.readFileSync(path.join(root,'data/pages.json')));
const routes={'/data/jobs.json':'jobs','/data/sources.json':'sources','/data/pages.json':'pages','/data/exam-updates.json':'exam-updates','/data/regions.json':'regions','/data/notice-watch.json':'notice-watch','/data/auto-notices.json':'auto-notices','/data/ads-config.json':'ads-config','/data/editorial-pages.json':'editorial-pages'};
const bundle=Object.fromEntries(Object.entries(routes).map(([url,name])=>[url,JSON.parse(fs.readFileSync(path.join(root,'data',name+'.json')))]));
const url=pathToFileURL(path.join(root,'assets/js/app.mjs')).href;
const values={};
globalThis.localStorage={getItem:k=>values[k]??null,setItem:(k,v)=>{values[k]=v}};
globalThis.history={replaceState:()=>{}};
const mocks={};
globalThis.document={body:{dataset:{page:'home'}},documentElement:{dataset:{}},getElementById(id){if(id==='app')return mocks.app;if(id==='jobpath-data')return {textContent:JSON.stringify(bundle)};return null},querySelector(){return null},addEventListener(){},createElement(){return {setAttribute(){},style:{}}}};
test('every configured route renders via complete embedded data, without fetching JSON',async()=>{
 let fails=[];
 for (const [page,meta] of Object.entries(pages)){
  mocks.app={innerHTML:'',querySelector(){return null}};
  document.body.dataset.page=page;
  const pathName='/'+(meta.path?meta.path+'/':'');
  globalThis.location={pathname:pathName,search:'',href:'https://jobpath-india.netlify.app'+pathName};
  globalThis.fetch=async()=>{throw Error('Network JSON unexpectedly attempted')};
  await import(url+'?test='+page);
  await new Promise(resolve=>setTimeout(resolve,0));
  let out=mocks.app.innerHTML;
  if(!out.includes('<main')||!out.includes('<h1')||out.includes('Page temporarily unavailable'))fails.push(page+': '+out.slice(0,100));
  if(page==='examupdates'&&(!out.includes('Sub-Inspector in Delhi Police')||!out.includes('class="exam-schedule-card"')||!out.includes('PROPOSED · NOT FINAL')))fails.push('Responsive SSC corrigendum cards/status missing');
  if(page==='statesdir'&&!out.includes('Lakshadweep'))fails.push('UT directory missing');
  if(page==='sources'&&!out.includes('source-search'))fails.push('source search missing');
  if(page==='careerguides'&&!out.includes('Railway recruitment regions'))fails.push('career pathways missing');
  if(page==='home'&&!out.includes('Verified vacancy records'))fails.push('homepage verification labels missing');
  if(page==='privacy'&&(!out.includes('Adsterra')||!out.includes('adsterra.com/privacy-policy-managed/')||!out.includes('Google AdSense')))fails.push('Current ad-provider disclosures missing');
 }
 assert.deepEqual(fails,[]);
});
test('demo records are opt-in and not included on the public home page',()=>{
 assert.equal(bundle['/data/jobs.json'].filter(x=>x.verified&&!x.isDemo).length,10);
 assert.equal(bundle['/data/regions.json'].states.length,28);
 assert.equal(bundle['/data/regions.json'].unionTerritories.length,8);
});
