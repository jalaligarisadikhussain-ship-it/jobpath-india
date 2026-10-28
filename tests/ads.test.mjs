import test from 'node:test';
import assert from 'node:assert/strict';
import {renderAdPlacement,adSenseReady} from '../assets/js/ads.mjs';
import fs from 'node:fs';

const current=JSON.parse(fs.readFileSync(new URL('../data/ads-config.json', import.meta.url),'utf8'));
const enabled={enabled:true,provider:'adsense',publisherId:'ca-pub-1234567890123456',slots:{content:'1234567890'}};

test('AdSense disabled until user has a real approved account',()=>{
 assert.equal(current.enabled,false);
 assert.equal(adSenseReady(current),false);
 assert.doesNotMatch(renderAdPlacement(current),/adsbygoogle|data-ad-client|data-ad-slot/);
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
test('only legitimate content positions have ad placements',()=>{
 assert.equal(renderAdPlacement(enabled,'jobDetail'),'');
 assert.equal(renderAdPlacement(enabled,'application'),'');
 assert.match(renderAdPlacement(enabled,'content'),/Advertisement/);
});
