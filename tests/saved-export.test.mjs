import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const app=fs.readFileSync('assets/js/app.mjs','utf8');
const start=app.indexOf('function exportSavedJobsCSV(){');
const end=app.indexOf('function deadlinePage(){',start);
assert(start>=0&&end>start,'Saved-job exporter must exist');
const code=app.slice(start,end);

test('local CSV export excludes demo records and neutralizes spreadsheet formulas',()=>{
 const jobs=[
  {id:'safe',title:'=HYPERLINK("https://example.invalid")',organization:'Issuer',state:'India',qualification:'Degree',lastDate:'2026-11-20',lastVerifiedDate:'2026-11-02',notificationUrl:'https://example.gov.in/notice',verified:true,isDemo:false},
  {id:'demo',title:'Invented Test Job',organization:'Fictional',verified:false,isDemo:true},
 ];
 let downloaded=null,filename=null;
 const context={
  jobs,saved:new Set(['safe','demo']),
  effectiveStatus:()=> 'open',
  safeUrl:u=>u?.startsWith('https://')?u:null,
  toast:()=>{},setTimeout:()=>{},
  URL:{createObjectURL:b=>{downloaded=b.contents;return 'blob:local'},revokeObjectURL:()=>{}},
  Blob:class {constructor(parts){this.contents=parts.join('')}},
  document:{body:{append:()=>{}},createElement:()=>({hidden:false,click(){filename=this.download},remove(){}})}
 };
 vm.runInNewContext(code+'; exportSavedJobsCSV();',context);
 assert.equal(filename,'jobpath-reviewed-saved-jobs.csv');
 assert.match(downloaded,/"'=HYPERLINK/);
 assert.match(downloaded,/example\.gov\.in/);
 assert.doesNotMatch(downloaded,/Invented Test Job|Fictional/);
 assert.match(app,/data-export-saved/);
});
