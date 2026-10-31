import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {ADSTERRA_KEY,ADSTERRA_SCRIPT,AD_CONSENT_KEY,AD_CONSENT_VERSION,
 adsterraConfigured,adsterraReady,advertisingReady,renderAdPlacement,
 readAdvertisingConsent,saveAdvertisingConsent,startAdUnits,chooseAdvertising,
 resolveAdvertisingConfig,monitorNativeFill,effectiveAdvertisingChoice,CLOUDFLARE_ADSTERRA_HOST,CLOUDFLARE_ADSTERRA_SCRIPT,CLOUDFLARE_ADSTERRA_KEY} from '../assets/js/ads.mjs';

const current=JSON.parse(fs.readFileSync(new URL('../data/ads-config.json',import.meta.url)));
// Test activation only; these tests never load a third-party script or create impressions.
const active={...current,enabled:true,provider:'adsterra',adsterra:{...current.adsterra,gamblingExclusionConfirmed:true}};
function memoryStorage(){
 const values=new Map();
 return {getItem:key=>values.get(key)??null,setItem:(key,value)=>values.set(key,value)};
}
function browserFixture(run,options={}){
 const previous={window:globalThis.window,document:globalThis.document,localStorage:globalThis.localStorage};
 const storage=memoryStorage(),scripts=[],notice={},status={textContent:''};let reloads=0;
 const targetKey=options.key||ADSTERRA_KEY, targetHost=options.hostname||'jobpath-india.netlify.app';
 const targetScript=options.script||ADSTERRA_SCRIPT;
 const parent={querySelector:()=>status,insertBefore:(script,node)=>{assert.equal(node,unit);scripts.push(script)}};
 const unit={id:'container-'+targetKey,dataset:{},parentNode:parent,hidden:true};
 const host={dataset:{},querySelector:selector=>selector==='[data-ad-consent-notice]'?notice:selector==='[data-jobpath-native]'?unit:status};
 globalThis.localStorage=storage;
 globalThis.window={navigator:{globalPrivacyControl:false},location:{hostname:targetHost,reload:()=>reloads++}};
 globalThis.document={
  querySelectorAll:selector=>selector==='[data-jobpath-native-placement]'?[host]:selector==='[data-jobpath-native]'?[unit]:[],
  querySelector:selector=>selector==='script[src="'+targetScript+'"]'?scripts[0]??null:null,
  getElementById:()=>null,
  createElement:tag=>{assert.equal(tag,'script');return {attrs:{},setAttribute(name,value){this.attrs[name]=value},addEventListener(){}}}
 };
 try{run({storage,scripts,unit,host,notice,status,reloads:()=>reloads})}
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
 assert.equal(adsterraReady({...active,adsterra:{...active.adsterra,websiteId:'6156497'}}),false);
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
 assert.doesNotMatch(html,/Allow advertising|Continue without ads|Show sponsored ads/);
 assert.doesNotMatch(html,/<script|<iframe|Official apply|Apply Now/);
 assert.equal(renderAdPlacement(active,'application'),'');
 assert.equal(renderAdPlacement(active,'jobDetail'),'');
});

test('Cloudflare publisher-authorized automatic ads retain visitor opt-out',()=>{
 const cloud=resolveAdvertisingConfig(current,CLOUDFLARE_ADSTERRA_HOST);
 assert.equal(current.cloudflareAdsterra.enabled,true);
 assert.equal(current.cloudflareAdsterra.userAuthorizedTrial,true);
 assert.equal(current.cloudflareAdsterra.datingExclusionConfirmed,false);
 assert.equal(current.cloudflareAdsterra.gamblingExclusionConfirmed,false);
 assert.equal(cloud.enabled,true);
 assert.equal(cloud.provider,'adsterra');
 assert.equal(adsterraReady(cloud),true);
 assert.match(renderAdPlacement(cloud,'top'),/Advertisement/);
 assert.doesNotMatch(renderAdPlacement(cloud,'top'),/Allow advertising|Continue without ads/);
 assert.equal(cloud.consent.required,false);
 assert.equal(cloud.adsterra.automaticDisplay,true);
 const other=resolveAdvertisingConfig(current,'jobpath-india.netlify.app');
 assert.equal(other.enabled,false);
});
test('Cloudflare trial rejects missing authorization, wrong host, tampered code and inactive units',()=>{
 for(const patch of [
  {enabled:false},{userAuthorizedTrial:false},{allowUnfilteredCategories:false},
  {siteStatus:'rejected'},{adUnitStatus:'inactive'},{adultAds:true},
  {scriptUrl:'https://example.com/inject.js'},{websiteHost:'example.com'}
 ]){
  const altered={...current,cloudflareAdsterra:{...current.cloudflareAdsterra,...patch}};
  const resolved=resolveAdvertisingConfig(altered,CLOUDFLARE_ADSTERRA_HOST);
  assert.equal(adsterraReady(resolved),false);
 }
});
test('Cloudflare persisted refusal blocks automatic ad scripts',()=>browserFixture(({storage,scripts,unit})=>{
 const cloud=resolveAdvertisingConfig(current,CLOUDFLARE_ADSTERRA_HOST);
 saveAdvertisingConsent('deny',storage);
 assert.equal(effectiveAdvertisingChoice(cloud,storage),'deny');
 assert.equal(startAdUnits(cloud),0);
 assert.equal(scripts.length,0);
 assert.equal(unit.hidden,true);
},{hostname:CLOUDFLARE_ADSTERRA_HOST,key:CLOUDFLARE_ADSTERRA_KEY,script:CLOUDFLARE_ADSTERRA_SCRIPT}));
test('Cloudflare default display loads pinned ad tag without homepage permission button',()=>browserFixture(({storage,scripts,unit})=>{
 const cloud=resolveAdvertisingConfig(current,CLOUDFLARE_ADSTERRA_HOST);
 assert.equal(effectiveAdvertisingChoice(cloud,storage),'allow');
 assert.equal(startAdUnits(cloud),1);
 assert.equal(unit.hidden,false);
 assert.equal(scripts[0].src,CLOUDFLARE_ADSTERRA_SCRIPT);
 assert.equal(startAdUnits(cloud),0);
 assert.equal(scripts.length,1);
},{hostname:CLOUDFLARE_ADSTERRA_HOST,key:CLOUDFLARE_ADSTERRA_KEY,script:CLOUDFLARE_ADSTERRA_SCRIPT}));
test('Cloudflare defaults never bypass GPC, storage failures or another host',()=>{
 const cloud=resolveAdvertisingConfig(current,CLOUDFLARE_ADSTERRA_HOST);
 const stored=memoryStorage(),prior=globalThis.window;
 try{
  globalThis.window={navigator:{globalPrivacyControl:false}};
  assert.equal(effectiveAdvertisingChoice(cloud,stored),'allow');
  assert.equal(effectiveAdvertisingChoice(active,stored),null);
  assert.equal(effectiveAdvertisingChoice(cloud,{getItem(){throw Error('blocked')}}),null);
  saveAdvertisingConsent('deny',stored);
  assert.equal(effectiveAdvertisingChoice(cloud,stored),'deny');
  saveAdvertisingConsent('allow',stored);
  assert.equal(effectiveAdvertisingChoice(cloud,stored),'allow');
  globalThis.window.navigator.globalPrivacyControl=true;
  assert.equal(effectiveAdvertisingChoice(cloud,stored),'deny');
 }finally{if(prior===undefined)delete globalThis.window;else globalThis.window=prior}
});
test('Even configured ads fail closed without actual gambling exclusion',()=>{
 assert.equal(adsterraReady({...active,adsterra:{...active.adsterra,gamblingExclusionConfirmed:false}}),false);
 assert.equal(adsterraReady({...active,adsterra:{...active.adsterra,siteStatus:'unverified'}}),false);
});

test('Declining a native ad collapses its panel, and opting back in restores it',()=>browserFixture(({storage,unit,host,notice})=>{
 saveAdvertisingConsent('deny',storage);assert.equal(startAdUnits(active),0);
 assert.equal(host.hidden,true);assert.equal(unit.hidden,true);assert.equal(notice.hidden,true);
 saveAdvertisingConsent('allow',storage);assert.equal(startAdUnits(active),1);
 assert.equal(host.hidden,false);assert.equal(host.dataset.adState,'active');assert.equal(unit.hidden,false);
}));
test('Native sponsorship notice is compact, clearly marked and not an application',()=>{
 const markup=renderAdPlacement(active,'top');
 assert.match(markup,/Advertisement/);assert.doesNotMatch(markup,/Allow advertising|Show sponsored ads/);
 assert.doesNotMatch(markup,/<iframe|Official apply|Apply Now/);
 const css=fs.readFileSync(new URL('../assets/css/styles.css',import.meta.url),'utf8');
 assert.match(css,/\.top-ad-region \.ad-placement\[hidden\]/);
 assert.match(css,/\.analytics-consent\{width:min\(375px/);
});

test('Adsterra prohibition: custom publisher iframe banners cannot load on any host',()=>{
 const cfg=JSON.parse(fs.readFileSync(new URL('../data/ads-config.json',import.meta.url)));
 const cloud=resolveAdvertisingConfig(cfg,CLOUDFLARE_ADSTERRA_HOST);
 const app=fs.readFileSync(new URL('../assets/js/app.mjs',import.meta.url),'utf8');
 const ads=fs.readFileSync(new URL('../assets/js/ads.mjs',import.meta.url),'utf8');
 const build=fs.readFileSync(new URL('../scripts/build_dist.py',import.meta.url),'utf8');
 assert.equal(cfg.cloudflareBanners.enabled,false);
 assert.equal(cfg.plannedPlacements.filter(x=>x.enabled).length,1);
 assert.equal(cfg.plannedPlacements.find(x=>x.enabled).id,'homepage-bottom');
 assert.equal(adsterraReady(cloud),true); // original direct Native Banner preserved
 assert.ok(!app.includes('siteBanner('));
 assert.ok(!app.includes('monitorBannerFill('));
 assert.ok(!ads.includes('renderBannerPlacement('));
 assert.ok(!ads.includes('data-jp-banner-frame'));
 assert.match(build,/assert ads_config\['cloudflareBanners'\]\['enabled'\] is False/);
 assert.doesNotMatch(build,/var atOptions =|jobpath-banner-fill/);
 assert.match(app,/\$\{topAd\(\)\}<section class="hero">/);
});
test('Cloudflare banner code IDs retained for reference only; no page-level iframe is created',()=>{
 const cfg=JSON.parse(fs.readFileSync(new URL('../data/ads-config.json',import.meta.url)));
 assert.deepEqual(Object.keys(cfg.cloudflareBanners.units).sort(),['desktop','mobile','rectangle']);
 assert.equal(cfg.cloudflareBanners.enabled,false);
 const build=fs.readFileSync(new URL('../scripts/build_dist.py',import.meta.url),'utf8');
 assert.doesNotMatch(build,/ad_dir\s*=|ad-units\//);
});
test('native ad remains invisible until real content, and empty slot collapses',()=>{
 const callbacks=[];
 const win={setTimeout:(cb,delay)=>{callbacks.push({cb,delay});return callbacks.length}};
 const unit=()=>({querySelectorAll:()=>[]});
 const empty=unit();
 const emptyHost={hidden:false,dataset:{adState:'active'},querySelector:()=>empty};
 const creative={querySelectorAll:selector=>selector==='img,canvas,video'?
  [{tagName:'IMG',complete:true,naturalWidth:300,naturalHeight:250}]:[]};
 const filledHost={hidden:false,dataset:{adState:'active'},querySelector:()=>creative};
 const root={querySelectorAll:()=>[emptyHost,filledHost]};
 assert.equal(monitorNativeFill(root,win),2);
 assert.equal(emptyHost.dataset.jpNativeReady,'pending');
 assert.equal(filledHost.dataset.jpNativeReady,'filled');
 assert.equal(monitorNativeFill(root,win),0);
 callbacks.filter(x=>x.delay===8500).forEach(x=>x.cb());
 assert.equal(emptyHost.dataset.jpNativeReady,'empty');
 assert.equal(emptyHost.hidden,true);
 assert.equal(filledHost.hidden,false);
 assert.equal(filledHost.dataset.jpNativeReady,'filled');
 const inactive={hidden:false,dataset:{adState:'preview'},querySelector:()=>empty};
 assert.equal(monitorNativeFill({querySelectorAll:()=>[inactive]},win),0);
 // Iframe creatives are common for native providers; they must not be
 // mistaken for permanent no-fill and hidden before users can view them.
 const framed={
  querySelectorAll:sel=>sel==='iframe'?
   [{width:300,getAttribute:key=>key==='src'?'https://ads.example/creative':null}]:[]
 };
 const frameHost={hidden:false,dataset:{adState:'active'},querySelector:()=>framed};
 assert.equal(monitorNativeFill({querySelectorAll:()=>[frameHost]},win),1);
 assert.equal(frameHost.dataset.jpNativeReady,'filled');
});
test('Native fill detector still collapses an empty ad placement',()=>{
 const ads=fs.readFileSync(new URL('../assets/js/ads.mjs',import.meta.url),'utf8');
 assert.match(ads,/8500/);
 assert.match(ads,/jpNativeReady='empty'/);
});
