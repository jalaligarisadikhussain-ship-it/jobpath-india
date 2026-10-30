import test from 'node:test';
import assert from 'node:assert/strict';
import {renderAdPlacement,adSenseReady,advertisingReady} from '../assets/js/ads.mjs';
import fs from 'node:fs';

const current=JSON.parse(fs.readFileSync(new URL('../data/ads-config.json', import.meta.url),'utf8'));
const enabled={enabled:true,provider:'adsense',publisherId:'ca-pub-1234567890123456',slots:{content:'1234567890'}};

test('Ads are absent while configuration is disabled and only render with valid IDs',()=>{
 if(current.enabled){
  assert.equal(advertisingReady(current),true);
  assert.match(renderAdPlacement(current),/aria-label="Advertisement"/);
 }else{
  assert.equal(adSenseReady(current),false);
  assert.doesNotMatch(renderAdPlacement(current),/adsbygoogle|data-ad-client|data-ad-slot/);
 }
});
test('valid AdSense settings show labeled isolated display ads',()=>{
 const html=renderAdPlacement(enabled);
 assert.equal(adSenseReady(enabled),true);
 assert.match(html,/aria-label="Advertisement"/);
 assert.match(html,/data-ad-client="ca-pub-1234567890123456"/);
 assert.match(html,/data-ad-slot="1234567890"/);
 assert.doesNotMatch(html,/Apply Now|Official Apply|Recruitment Notification/);
});
test('script injection and malformed account IDs cannot turn ads on',()=>{
 for(const publisherId of ['ca-pub-abc', '<script>alert(1)</script>', 'pub-12345']){
  assert.equal(adSenseReady({...enabled,publisherId}),false);
 }
 assert.equal(adSenseReady({...enabled,slots:{content:'12" onload="alert(1)'}}),false);
 assert.equal(adSenseReady({...enabled,provider:'other'}),false);
});
test('top ads use a labeled in-flow slot, but disabled campaigns create no blank header space',()=>{
 assert.equal(renderAdPlacement(current,'top'),'');
 const top=renderAdPlacement(enabled,'top');
 assert.match(top,/ad-placement-top/);
 assert.match(top,/aria-label="Advertisement"/);
 assert.match(top,/data-jobpath-ad="content"/);
 assert.doesNotMatch(top,/<script|<iframe/);
 const app=fs.readFileSync(new URL('../assets/js/app.mjs',import.meta.url),'utf8');
 assert.match(app,/header\(\)\+\(PAGE===/);
 assert.match(app,/function ad\(\)\{return ''\}/);
});
test('only legitimate content positions have ad placements',()=>{
 assert.equal(renderAdPlacement(enabled,'jobDetail'),'');
 assert.equal(renderAdPlacement(enabled,'application'),'');
 assert.match(renderAdPlacement(enabled,'content'),/Advertisement/);
});
