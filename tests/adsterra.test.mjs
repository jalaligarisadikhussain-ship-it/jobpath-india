import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {ADSTERRA_KEY,ADSTERRA_SCRIPT,AD_CONSENT_KEY,AD_CONSENT_VERSION,
 adsterraConfigured,adsterraReady,advertisingReady,renderAdPlacement,
 readAdvertisingConsent,saveAdvertisingConsent,startAdUnits,chooseAdvertising,
 resolveAdvertisingConfig,bannerReady,renderBannerPlacement,CLOUDFLARE_ADSTERRA_HOST,CLOUDFLARE_ADSTERRA_SCRIPT,CLOUDFLARE_ADSTERRA_KEY} from '../assets/js/ads.mjs';

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
 assert.match(html,/Allow advertising/);assert.match(html,/Continue without ads/);
 assert.doesNotMatch(html,/<script|<iframe|Official apply|Apply Now/);
 assert.equal(renderAdPlacement(active,'application'),'');
 assert.equal(renderAdPlacement(active,'jobDetail'),'');
});

test('Cloudflare trial requires explicit publisher authorization and renewed visitor consent',()=>{
 const cloud=resolveAdvertisingConfig(current,CLOUDFLARE_ADSTERRA_HOST);
 assert.equal(current.cloudflareAdsterra.enabled,true);
 assert.equal(current.cloudflareAdsterra.userAuthorizedTrial,true);
 assert.equal(current.cloudflareAdsterra.datingExclusionConfirmed,false);
 assert.equal(current.cloudflareAdsterra.gamblingExclusionConfirmed,false);
 assert.equal(cloud.enabled,true);
 assert.equal(cloud.provider,'adsterra');
 assert.equal(adsterraReady(cloud),true);
 assert.match(renderAdPlacement(cloud,'top'),/Advertisement/);
 assert.match(renderAdPlacement(cloud,'top'),/dating-style content/);
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
test('Previously saved opt-in from earlier version cannot load ads',()=>browserFixture(({storage,scripts,unit})=>{
 window.location.hostname=CLOUDFLARE_ADSTERRA_HOST;
 storage.setItem(AD_CONSENT_KEY,JSON.stringify({version:'adsterra-2026-10-29',choice:'allow',timestamp:Date.now()}));
 const cloud=resolveAdvertisingConfig(current,CLOUDFLARE_ADSTERRA_HOST);
 assert.equal(startAdUnits(cloud),0);
 assert.equal(scripts.length,0);
 assert.equal(unit.hidden,true);
},{hostname:CLOUDFLARE_ADSTERRA_HOST,key:CLOUDFLARE_ADSTERRA_KEY,script:CLOUDFLARE_ADSTERRA_SCRIPT}));
test('Cloudflare opt-in trial injects only the pinned ad tag on its exact domain',()=>browserFixture(({storage,scripts,unit})=>{
 const cloud=resolveAdvertisingConfig(current,CLOUDFLARE_ADSTERRA_HOST);
 assert.equal(startAdUnits(cloud),0);
 saveAdvertisingConsent('allow',storage);
 assert.equal(startAdUnits(cloud),1);
 assert.equal(unit.hidden,false);
 assert.equal(scripts[0].src,CLOUDFLARE_ADSTERRA_SCRIPT);
 assert.equal(startAdUnits(cloud),0);
 assert.equal(scripts.length,1);
},{hostname:CLOUDFLARE_ADSTERRA_HOST,key:CLOUDFLARE_ADSTERRA_KEY,script:CLOUDFLARE_ADSTERRA_SCRIPT}));
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
 assert.match(markup,/Optional sponsored content/);assert.match(markup,/Advertisement/);
 assert.doesNotMatch(markup,/<iframe|Official apply|Apply Now/);
 const css=fs.readFileSync(new URL('../assets/css/styles.css',import.meta.url),'utf8');
 assert.match(css,/\.top-ad-region \.ad-placement\[hidden\]/);
 assert.match(css,/\.analytics-consent\{width:min\(375px/);
});

test('ad positions stay ordered while unverified top and middle banners are hidden',()=>{
 const app=fs.readFileSync(new URL('../assets/js/app.mjs',import.meta.url),'utf8');
 const homepage=app.slice(app.indexOf('function home()'),app.indexOf('function options('));
 const first=homepage.indexOf('siteBanner("responsive")');
 const hero=homepage.indexOf('<section class="hero">');
 const categories=homepage.indexOf("Explore by career path");
 const middle=homepage.indexOf("siteBanner('rectangle')");
 const vacancies=homepage.indexOf("Latest reviewed vacancies");
 const exams=homepage.indexOf("Examination resources");
 const last=homepage.indexOf('topAd()');
 assert.ok(first>=0&&first<hero);
 assert.ok(categories<middle&&middle<vacancies);
 assert.ok(exams<last&&last>middle);
 assert.equal(homepage.split('siteBanner("responsive")').length-1,1);
 assert.equal(homepage.split("siteBanner('rectangle')").length-1,1);
 assert.equal(homepage.split('topAd()').length-1,1);
 const cfg=JSON.parse(fs.readFileSync(new URL('../data/ads-config.json',import.meta.url),'utf8'));
 assert.deepEqual(cfg.plannedPlacements.map(x=>x.id),
 ['homepage-top','homepage-middle','homepage-bottom']);
 assert.equal(cfg.plannedPlacements.filter(x=>x.enabled).length,1);
 assert.equal(cfg.cloudflareBanners.deliveryVerified,false);
 assert.equal(cfg.cloudflareAdsterra.datingExclusionConfirmed,false);
});

test('homepage offers a compact in-flow consent choice and never auto-loads ads',()=>{
 const app=fs.readFileSync(new URL('../assets/js/app.mjs',import.meta.url),'utf8');
 assert.match(app,/function adQuickAccess\(\)/);
 assert.match(app,/readAdvertisingConsent\(\)!=='allow'/);
 assert.match(app,/data-ad-choice="allow"/);
 assert.match(app,/data-ad-choice="deny"/);
 assert.match(app,/return `\$\{siteBanner\("responsive"\)\}<section class="hero">/);
 assert.match(app,/<\/section>\$\{adQuickAccess\(\)\}<div class="stats">/);
 assert.match(app,/PAGE==="home"\?"":topAd\(\)/);
 assert.doesNotMatch(app,/header\(\)\+topAd\(\)/);
});

test('unverified fixed banners do not render white ad placeholders or request impressions',()=>{
 const cfg=JSON.parse(fs.readFileSync(new URL('../data/ads-config.json',import.meta.url),'utf8'));
 const resolved=resolveAdvertisingConfig(cfg,CLOUDFLARE_ADSTERRA_HOST);
 assert.equal(cfg.cloudflareBanners.deliveryVerified,false);
 assert.equal(bannerReady(resolved),false);
 assert.equal(renderBannerPlacement(resolved,'responsive',CLOUDFLARE_ADSTERRA_HOST,'allow'),'');
 assert.equal(renderBannerPlacement(resolved,'rectangle',CLOUDFLARE_ADSTERRA_HOST,'allow'),'');
 assert.equal(renderBannerPlacement(resolved,'responsive',CLOUDFLARE_ADSTERRA_HOST,''),'');
 assert.equal(renderBannerPlacement(resolved,'rectangle','jobpath-india.netlify.app','allow'),'');
 // Provider-code validation remains available for a future manual verification.
 const simulated={...resolved,cloudflareBanners:{...resolved.cloudflareBanners,deliveryVerified:true}};
 assert.equal(bannerReady(simulated),true);
 const wide=renderBannerPlacement(simulated,'responsive',CLOUDFLARE_ADSTERRA_HOST,'allow');
 assert.ok(wide.includes('ad-units/desktop.html'));
 assert.ok(!wide.includes('ad-units/mobile.html'));
 const prior=globalThis.window;
 try{globalThis.window={matchMedia:()=>({matches:true})};
  assert.ok(renderBannerPlacement(simulated,'responsive',CLOUDFLARE_ADSTERRA_HOST,'allow').includes('ad-units/mobile.html'));
 }finally{if(prior===undefined)delete globalThis.window;else globalThis.window=prior}
 assert.ok(renderBannerPlacement(simulated,'rectangle',CLOUDFLARE_ADSTERRA_HOST,'allow').includes('ad-units/rectangle.html'));
 const tampered={...simulated,cloudflareBanners:{...simulated.cloudflareBanners,units:{...simulated.cloudflareBanners.units,mobile:{...simulated.cloudflareBanners.units.mobile,key:'tampered'}}}};
 assert.equal(bannerReady(tampered),false);
});

test('unfilled display inventory collapses rather than leaving white ad boxes',()=>{
 const s=fs.readFileSync(new URL('../assets/js/ads.mjs',import.meta.url),'utf8');
 const css=fs.readFileSync(new URL('../assets/css/styles.css',import.meta.url),'utf8');
 const builder=fs.readFileSync(new URL('../scripts/build_dist.py',import.meta.url),'utf8');
 assert.match(s,/export function monitorBannerFill\(/);
 assert.match(s,/node\.querySelector\('iframe\[data-jp-banner-frame\]'\)\?\.contentWindow===event\.source/);
 assert.match(s,/slot\.hidden=true/);
 assert.match(s,/IntersectionObserver/);
 assert.match(css,/\.jp-banner\[hidden\]/);
 assert.match(builder,/jobpath-banner-fill/);
 assert.match(builder,/creative\(\)/);
});

test('blank iframe-only markup is not treated as a filled advertisement',()=>{
 const build=fs.readFileSync(new URL('../scripts/build_dist.py',import.meta.url),'utf8');
 const runtime=fs.readFileSync(new URL('../assets/js/ads.mjs',import.meta.url),'utf8');
 const css=fs.readFileSync(new URL('../assets/css/styles.css',import.meta.url),'utf8');
 assert.match(build,/An iframe existing is NOT proof/);
 assert.doesNotMatch(build,/el\.tagName==='IFRAME'.*return true/);
 assert.match(build,/naturalWidth>=90/);
 assert.match(build,/report\('empty'\)/);
 assert.match(runtime,/slot\.dataset\.jpBannerState='empty';slot\.hidden=true/);
 assert.match(runtime,/5700/);
 assert.match(css,/\.jp-banner\[data-jp-banner-state="empty"\]/);
});

test('new ad-fix deploy invalidates old cached site script and ad iframe assets',()=>{
 const build=fs.readFileSync(new URL('../scripts/build_final.py',import.meta.url),'utf8');
 const app=fs.readFileSync(new URL('../assets/js/app.mjs',import.meta.url),'utf8');
 const ads=fs.readFileSync(new URL('../assets/js/ads.mjs',import.meta.url),'utf8');
 assert.match(build,/styles\.css\?v=ads-verified-only-20261031/);
 assert.match(build,/app\.mjs\?v=ads-verified-only-20261031/);
 assert.match(app,/ads\.mjs\?v=ads-verified-only-20261031/);
 assert.match(ads,/ad-units\/.*ads-verified-only-20261031/);
});
