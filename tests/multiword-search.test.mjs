import test from 'node:test';
import assert from 'node:assert/strict';
import {filterJobs} from '../assets/js/utils.mjs';

const jobs=[
 {id:'rail',title:'Junior Engineer',organization:'Railway Recruitment Board',state:'All India',department:'Engineering',category:'Railway',qualification:'Diploma',type:'Central',verified:true,status:'open',lastDate:'2027-02-04',publishedDate:'2026-11-02'},
 {id:'exam',title:'Assistant Manager',organization:'Central Warehousing Corporation',state:'All India',department:'Administration',category:'PSU',qualification:'Postgraduate',type:'Central',verified:true,status:'open',lastDate:'2027-02-12',publishedDate:'2026-11-02'}
];
const now=new Date('2026-11-02T12:00:00Z');

test('search every keyword across role and organization rather than contiguous phrase',()=>{
 assert.deepEqual(filterJobs(jobs,{q:'railway engineer'},now).map(x=>x.id),['rail']);
 assert.deepEqual(filterJobs(jobs,{q:'manager central'},now).map(x=>x.id),['exam']);
 assert.deepEqual(filterJobs(jobs,{q:'railway manager'},now),[]);
 assert.deepEqual(filterJobs(jobs,{q:'  ENGINEER    railway  '},now).map(x=>x.id),['rail']);
});

test('existing status, qualification and deadline filtering still work',()=>{
 assert.deepEqual(filterJobs(jobs,{qualification:'Diploma',deadline:'future'},now).map(x=>x.id),['rail']);
 assert.equal(filterJobs(jobs,{status:'closed'},now).length,0);
});
