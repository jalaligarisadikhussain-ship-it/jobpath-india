import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {effectiveStatus,publicJobs} from '../assets/js/utils.mjs';

const app=fs.readFileSync('assets/js/app.mjs','utf8');
const now=new Date('2026-11-02T12:00:00Z');
const fake=[
 {id:'open',title:'Open',verified:true,isDemo:false,status:'open',lastDate:'2026-11-09'},
 {id:'expired',title:'Expired',verified:true,isDemo:false,status:'open',lastDate:'2026-11-01'},
 {id:'closed',title:'Closed',verified:true,isDemo:false,status:'closed',lastDate:'2026-11-10'},
 {id:'demo',title:'Demo',verified:false,isDemo:true,status:'open',lastDate:'2026-11-12'}
];

test('homepage open-vacancy policy excludes demo, expired, closed listings',()=>{
 const eligible=publicJobs(fake,false).filter(j=>effectiveStatus(j,now)==='open');
 assert.deepEqual(eligible.map(j=>j.id),['open']);
 assert.match(app,/function home\(\)\{const realJobs=publicJobs\(jobs,false\)\.filter\(j=>effectiveStatus\(j\)==='open'\)/);
 assert.match(app,/\.sort\(\(a,b\)=>\(a\.lastDate\|\|'9999-12-31'\)/);
});

test('homepage never promises that unrelated ads are automatically blocked',()=>{
 assert.doesNotMatch(app,/No dating, gambling or unrelated promotions\./);
 assert.match(app,/Report any inappropriate ad you see/);
 assert.match(app,/issues\/new\?template=ad-quality\.yml/);
});
