import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {ADSTERRA_KEY,ADSTERRA_SCRIPT,AD_CONSENT_KEY,AD_CONSENT_VERSION,
 adsterraConfigured,adsterraReady,advertisingReady,renderAdPlacement,
 readAdvertisingConsent,saveAdvertisingConsent,startAdUnits,chooseAdvertising} from '../assets/js/ads.mjs';

const current=JSON.parse(fs.readFileSync(new URL('../data/ads-config.json',import.meta.url)));
// Test activation only; these tests never load a third-party script or create impressions.
const active={...current,enabled:true,provider:'adsterra',adsterra:{...current.adsterra,siteStatus:'approved'}};
function memoryStorage(){
 const values=new Map();
 return {getItem:key=>values.get(key)??null,setItem:(key,value)=>values.set(key,value)};
}
function browserFixture(run){
 const previous={window:globalThis.window,document:globalThis.document,localStorage:globalThis.localStorage};
 const storage=memoryStorage(),scripts=[],notice={},status={textContent:''};let reloads=0;
 const parent={querySelector:()=>status,insertBefore:(script,node)=>{assert.equal(node,unit);scripts.push(script)}};
 const unit={id:'container-'+ADSTERRA_KEY,dataset:{},parentNode:parent,hidden:true};
 const host={querySelector:selector=>selector==='[data-ad-consent-notice]'?notice:selector==='[data-jobpath-native]'?unit:status};
 globalThis.localStorage=storage;
 globalThis.window={navigator:{globalPrivacyControl:false},location:{hostname:'jobpath-india.pages.dev',reload:()=>reloads++}};
 globalThis.document={
  querySelectorAll:selector=>selector==='[data-jobpath-native-placement]'?[host]:selector==='[data-jobpath-native]'?[unit]:[],
  querySelector:selector=>selector==='script[src="'+ADSTERRA_SCRIPT+'"]'?scripts[0]??null:null,
  getElementById:()=>null,
  createElement:tag=>{assert.equal(tag,'script');return {attrs:{},setAttribute(name,value){this.attrs[name]=value},addEventListener(){}}}
 };
 try{run({storage,scripts,unit,notice,status,reloads:()=>reloads})}
 finally{for(const [key,value] of Object.entries(previous)){if(value===undefined)delete globalThis[key];else globalThis[key]=value}}
}

test('the verified native tag is prepared separately from live activation',()=>{
 assert.equal(adsterraConfigured(current),true);
 const disabled={...current,enabled:false,provider:'none'};
 assert.equal(advertisingReady(disabled),false);
 assert.equal(adsterraReady(active),true);
 assert.doesNotMatch(renderAdPlacement(disabled),/data-jobpath-native|<script|<iframe/);
});
test('another project, altered script URL and unapproved unit cannot activate',()=>{
 for(const scriptUrl of ['https://example.com/ad.js',ADSTERRA_SCRIPT+'?track=1',ADSTERRA_SCRIPT+'"><script>']){
  assert.equal(adsterraReady({...active,adsterra:{...active.adsterra,scriptUrl}}),false);
 }
 assert.equal(adsterraReady({...active,adsterra:{...active.adsterra,websiteHost:'example.com'}}),false);
 assert.equal(adsterraReady({...active,adsterra:{...active.adsterra,siteStatus:'pending'}}),false);
 assert.equal(adsterraReady({...active,adsterra:{...active.adsterra,adUnitStatus:'inactive'}}),false);
 assert.equal(adsterraReady({...active,consent:{required:false,version:AD_CONSENT_VERSION}}),false);
});
test('consent defaults off and rejects stale, malformed or future records',()=>{
 const storage=memoryStorage(),now=1793239200000;
 assert.equal(readAdvertisingConsent(storage,now),null);
 for(const value of ['bad json',JSON.stringify({version:'old',choice:'allow',timestamp:now}),
  JSON.stringify({version:AD_CONSENT_VERSION,choice:'allow',timestamp:now+1}),
  JSON.stringify({version:AD_CONSENT_VERSION,choice:'allow',timestamp:now-181*86400000})]){
  storage.setItem(AD_CONSENT_KEY,value);assert.equal(readAdvertisingConsent(storage,now),null);
 }
 assert.equal(saveAdvertisingConsent('allow',storage,now),true);
 assert.equal(readAdvertisingConsent(storage,now), 'allow');
 assert.equal(saveAdvertisingConsent('deny',storage,now),true);
 assert.equal(readAdvertisingConsent(storage,now), 'deny');
 assert.equal(saveAdvertisingConsent('maybe',storage,now),false);
});
test('no script request is made without consent, after refusal or while disabled',()=>browserFixture(({storage,scripts,unit})=>{
 assert.equal(startAdUnits(active),0);
 assert.equal(unit.hidden,true);
 saveAdvertisingConsent('deny',storage);assert.equal(startAdUnits(active),0);
 saveAdvertisingConsent('allow',storage);assert.equal(startAdUnits({...current,enabled:false,provider:'none'}),0);
 assert.equal(scripts.length,0);
}));
test('opt-in inserts the exact approved tag once without an iframe',()=>browserFixture(({storage,scripts,unit})=>{
 saveAdvertisingConsent('allow',storage);
 assert.equal(startAdUnits(active),1);
 assert.equal(unit.hidden,false);
 assert.equal(scripts[0].src,ADSTERRA_SCRIPT);
 assert.deepEqual(scripts[0].attrs,{async:'async','data-cfasync':'false'});
 assert.equal(startAdUnits(active),0);
 assert.equal(scripts.length,1);
}));
test('withdrawal persists refusal and reloads to stop the active script',()=>browserFixture(({storage,scripts,reloads})=>{
 saveAdvertisingConsent('allow',storage);startAdUnits(active);
 assert.equal(chooseAdvertising(active,'deny'),true);
 assert.equal(readAdvertisingConsent(storage),'deny');
 assert.equal(reloads(),1);
 assert.equal(scripts.length,1);
}));
test('Global Privacy Control overrides a stored opt-in',()=>browserFixture(({storage,scripts})=>{
 saveAdvertisingConsent('allow',storage);window.navigator.globalPrivacyControl=true;
 assert.equal(startAdUnits(active),0);
 assert.equal(chooseAdvertising(active,'allow'),false);
 assert.equal(scripts.length,0);
}));
test('the tag cannot request ads from another website or a local test page',()=>browserFixture(({storage,scripts})=>{
 saveAdvertisingConsent('allow',storage);
 for(const hostname of ['localhost','bytebright-converter.netlify.app','example.com']){
  window.location.hostname=hostname;assert.equal(startAdUnits(active),0);
 }
 assert.equal(scripts.length,0);
}));
test('unavailable storage cannot silently grant consent',()=>browserFixture(({scripts})=>{
 globalThis.localStorage={getItem(){throw Error('blocked')},setItem(){throw Error('blocked')}};
 assert.equal(readAdvertisingConsent(),null);
 assert.equal(chooseAdvertising(active,'allow'),false);
 assert.equal(startAdUnits(active),0);
 assert.equal(scripts.length,0);
}));
test('a storage-access security error does not break the site or load ads',()=>browserFixture(({scripts})=>{
 const descriptor=Object.getOwnPropertyDescriptor(globalThis,'localStorage');
 Object.defineProperty(globalThis,'localStorage',{configurable:true,get(){throw Error('SecurityError')}});
 try{
  assert.equal(readAdvertisingConsent(),null);
  assert.equal(saveAdvertisingConsent('allow'),false);
  assert.equal(startAdUnits(active),0);
  assert.equal(scripts.length,0);
 }finally{Object.defineProperty(globalThis,'localStorage',descriptor)}
}));
test('native banners remain labeled, optional and outside application positions',()=>{
 const html=renderAdPlacement(active);
 assert.match(html,/aria-label="Advertisement"/);
 assert.match(html,/Allow advertising/);assert.match(html,/Continue without ads/);
 assert.doesNotMatch(html,/<script|<iframe|Official apply|Apply Now/);
 assert.equal(renderAdPlacement(active,'application'),'');
 assert.equal(renderAdPlacement(active,'jobDetail'),'');
});
