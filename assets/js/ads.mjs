/** Approved, project-specific tags. Third-party native ads require explicit opt-in. */
const PUBLISHER=/^ca-pub-[0-9]{16}$/;
const SLOT=/^[0-9]{8,12}$/;
export const ADSTERRA_KEY='59088646af2816821f7d8b37df198113';
export const ADSTERRA_SCRIPT='https://bauval.org/21/'+ADSTERRA_KEY;
export const ADSTERRA_HOST='jobpath-india.netlify.app';
export const CLOUDFLARE_ADSTERRA_HOST='jobpath-india.pages.dev';
export const CLOUDFLARE_ADSTERRA_KEY='84de856c9d01a37c08d4912fbf3df530';
export const CLOUDFLARE_ADSTERRA_SCRIPT='https://bauval.org/21/'+CLOUDFLARE_ADSTERRA_KEY;
export const AD_CONSENT_KEY='jp_advertising_consent';
export const AD_CONSENT_VERSION='adsterra-2026-10-30-trial';
const CONSENT_AGE=180*24*60*60*1000;

// Hosting-specific config: never change the existing Netlify/Render advertising state.
export function resolveAdvertisingConfig(config,hostname=''){
 if(hostname!==CLOUDFLARE_ADSTERRA_HOST)return config;
 const ad=config?.cloudflareAdsterra;
 // Publisher explicitly requested this opt-in trial even though provider-side
 // dating/gambling exclusions are unconfirmed. Do not claim category safety.
 const filtered=ad?.gamblingExclusionConfirmed===true&&ad.datingExclusionConfirmed===true&&
   ad.allowUnfilteredCategories!==true&&ad.siteStatus==='approved';
 const trial=ad?.userAuthorizedTrial===true&&ad.allowUnfilteredCategories===true&&
   ['approved','unverified'].includes(ad.siteStatus);
 if(ad?.enabled!==true||!(filtered||trial))return {...config,enabled:false,provider:'none'};
 return {...config,enabled:true,provider:'adsterra',adsterra:ad,
  consent:{required:true,version:AD_CONSENT_VERSION}};
}

export function adsterraConfigured(config){
 const ad=config?.adsterra;
 if(ad?.websiteHost===CLOUDFLARE_ADSTERRA_HOST){
  return ad.format==='native'&&ad.key===CLOUDFLARE_ADSTERRA_KEY&&
   ad.scriptUrl===CLOUDFLARE_ADSTERRA_SCRIPT&&
   ad.containerId==='container-'+CLOUDFLARE_ADSTERRA_KEY&&
   ad.adultAds===false&&ad.adUnitStatus==='active';
 }
 return ad?.websiteId==='6159057'&&ad.adUnitId==='31978670'&&ad.format==='native'&&
  ad.key===ADSTERRA_KEY&&ad.scriptUrl===ADSTERRA_SCRIPT&&
  ad.containerId==='container-'+ADSTERRA_KEY&&ad.adultAds===false;
}
export function adsterraReady(config){
 const ad=config?.adsterra;
 const isCloudflare=ad?.websiteHost===CLOUDFLARE_ADSTERRA_HOST;
 const filtered=ad?.gamblingExclusionConfirmed===true&&ad.siteStatus==='approved'&&
  (!isCloudflare||(ad.datingExclusionConfirmed===true&&ad.allowUnfilteredCategories!==true));
 const trial=isCloudflare&&ad?.userAuthorizedTrial===true&&ad.allowUnfilteredCategories===true&&
  ['approved','unverified'].includes(ad.siteStatus);
 return config?.enabled===true&&config.provider==='adsterra'&&adsterraConfigured(config)&&
  (filtered||trial)&&ad.adUnitStatus==='active'&&
  config.consent?.required===true&&config.consent.version===AD_CONSENT_VERSION;
}
// Exact jobpath-india.pages.dev banner codes supplied by the publisher.
const BANNER_KEYS=Object.freeze({"mobile":"22d5d7312497a4575a8261d0d18522ea","desktop":"5b1925f1b2ab32ef7b6d207bde9e0fa1","rectangle":"58623b07e46a924f55b4d5d4895086c0"});
export function bannerReady(config){
 const b=config?.cloudflareBanners;
 if(!adsterraReady(config)||b?.enabled!==true||b.websiteHost!==CLOUDFLARE_ADSTERRA_HOST)return false;
 for(const [name,key] of Object.entries(BANNER_KEYS)){
  const u=b.units?.[name],d={mobile:[320,50],desktop:[728,90],rectangle:[300,250]}[name];
  if(u?.enabled!==true||u.key!==key||u.format!=='iframe'||u.width!==d[0]||u.height!==d[1]||u.scriptUrl!=='https://bauval.org/22/'+key)return false;
 }
 return true;
}
export function renderBannerPlacement(config,location,hostname='',consent=''){
 if(!['responsive','rectangle'].includes(location)||hostname!==CLOUDFLARE_ADSTERRA_HOST||consent!=='allow'||!bannerReady(config))return '';
 if(typeof navigator!=='undefined'&&navigator.globalPrivacyControl===true)return '';
 const unit=name=>{const u=config.cloudflareBanners.units[name];
  return '<aside class="jp-banner jp-banner--'+name+'" data-jp-banner-unit="'+name+'" data-jp-banner-state="pending" aria-label="Advertisement"><span class="jp-banner-label">Advertisement</span>'+
   '<iframe loading="lazy" data-jp-banner-frame="'+name+'" title="Sponsored '+name+' banner" scrolling="no" referrerpolicy="strict-origin-when-cross-origin" sandbox="allow-scripts allow-popups" width="'+u.width+'" height="'+u.height+'" src="/ad-units/'+name+'.html"></iframe></aside>';};
 // Never request an impression for a hidden responsive format.
 const mobile=typeof window!=='undefined'&&window.matchMedia?.('(max-width:760px)')?.matches===true;
 return location==='responsive'?unit(mobile?'mobile':'desktop'):unit('rectangle');
}
// Blank ad inventory must not strand white cards on the job portal.
// Ad content comes from a sandboxed, site-hosted iframe. The iframe reports
// when a rendered creative exists; only a matching frame may update its slot.
export function monitorBannerFill(root=globalThis.document,win=globalThis.window){
 if(!root?.querySelectorAll||!win?.addEventListener)return 0;
 const slots=[...root.querySelectorAll('.jp-banner[data-jp-banner-unit]')];
 if(!slots.length)return 0;
 const timers=new Map();
 const collapse=slot=>{if(slot.dataset.jpBannerState==='filled')return;slot.dataset.jpBannerState='empty';slot.hidden=true;};
 const handler=event=>{
  const data=event.data;
  if(data?.type!=='jobpath-banner-fill'||!['filled','empty'].includes(data.status))return;
  const slot=slots.find(node=>node.dataset.jpBannerUnit===data.unit&&
   node.querySelector('iframe[data-jp-banner-frame]')?.contentWindow===event.source);
  if(!slot||slot.hidden)return;
  if(timers.has(slot)){clearTimeout(timers.get(slot));timers.delete(slot);}
  if(data.status==='filled'){slot.dataset.jpBannerState='filled';return;}
  collapse(slot);
 };
 win.addEventListener('message',handler);
 const watch=slot=>{if(slot.dataset.jpBannerWatching==='true')return;
  slot.dataset.jpBannerWatching='true';
  timers.set(slot,setTimeout(()=>{timers.delete(slot);collapse(slot);},8000));
 };
 if(typeof win.IntersectionObserver==='function'){
  const observer=new win.IntersectionObserver(entries=>{for(const entry of entries){
   if(entry.isIntersecting){watch(entry.target);observer.unobserve(entry.target);}
  }},{rootMargin:'260px'});
  slots.forEach(slot=>observer.observe(slot));
 } else slots.forEach(watch);
 return slots.length;
}
export function adSenseReady(config){
 return config?.enabled===true&&config.provider==='adsense'&&
   typeof config.publisherId==='string'&&PUBLISHER.test(config.publisherId)&&
   typeof config.slots?.content==='string'&&SLOT.test(config.slots.content);
}
export function advertisingReady(config){return adSenseReady(config)||adsterraReady(config)}
export function readAdvertisingConsent(storage,now=Date.now()){
 try{
  const target=storage===undefined?globalThis.localStorage:storage;
  const value=JSON.parse(target?.getItem(AD_CONSENT_KEY)||'null');
  if(value?.version!==AD_CONSENT_VERSION||!['allow','deny'].includes(value.choice)||
    !Number.isFinite(value.timestamp)||value.timestamp>now||now-value.timestamp>CONSENT_AGE)return null;
  return value.choice;
 }catch{return null}
}
export function saveAdvertisingConsent(choice,storage,now=Date.now()){
 if(!['allow','deny'].includes(choice))return false;
 try{const target=storage===undefined?globalThis.localStorage:storage;
  if(!target?.setItem)return false;
  target.setItem(AD_CONSENT_KEY,JSON.stringify({version:AD_CONSENT_VERSION,choice,timestamp:now}));
  return readAdvertisingConsent(target,now)===choice;
 }catch{return false}
}
function privacySignal(){return typeof window!=='undefined'&&window.navigator?.globalPrivacyControl===true}
const consentText='Adsterra ads are optional and may use cookies and device/browser information. The ad network has not confirmed restrictions on dating or other unwanted content, so such ads may reappear. You can decline and still use all job information.';
function consentButtons(){return '<div class="ad-consent-actions"><button type="button" class="btn btn-secondary" data-ad-choice="allow">Allow advertising</button><button type="button" class="btn btn-secondary" data-ad-choice="deny">Continue without ads</button></div>'}
export function renderAdPlacement(config,place='content'){
 if(!['content','top'].includes(place))return '';
 if(!advertisingReady(config))return ''; // No blank ad card for visitors while ads are disabled.
 if(adsterraReady(config))return '<aside class="ad-placement'+(place==='top'?' ad-placement-top':'')+'" aria-label="Advertisement" data-jobpath-native-placement>'+
  '<span class="ad-placement-label">Advertisement</span><div data-ad-consent-notice><div class="ad-consent-summary"><strong>Optional sponsored content</strong><p>Third-party ads may still contain unrelated or dating-style content until the ad network applies restrictions. Jobs remain free. <a href="/privacy-policy/">Privacy details</a>.</p></div>'+consentButtons()+'</div>'+
  '<div id="'+config.adsterra.containerId+'" data-jobpath-native hidden></div>'+
  '<p class="tiny muted" data-ad-status role="status"></p><button type="button" class="btn btn-ghost btn-sm" data-ad-choices>Advertising choices</button></aside>';
 // User-provided identifiers must pass strict numeric allowlists; no HTML interpolation of untrusted strings.
 return '<aside class="ad-placement'+(place==='top'?' ad-placement-top':'')+'" aria-label="Advertisement">'+
  '<span class="ad-placement-label">Advertisement</span>'+
  '<ins class="adsbygoogle" style="display:block" data-jobpath-ad="content" data-ad-client="'+
  config.publisherId+'" data-ad-slot="'+config.slots.content+
  '" data-ad-format="auto" data-full-width-responsive="true"></ins></aside>';
}
function syncNativePlacements(){
 const choice=readAdvertisingConsent(),blocked=privacySignal();
 for(const host of document.querySelectorAll('[data-jobpath-native-placement]')){
  // Decline or Global Privacy Control must not leave a blank ad panel.
  host.hidden=choice==='deny'||blocked;
  host.dataset.adState=blocked?'blocked':choice==='allow'?'active':'preview';
  const notice=host.querySelector('[data-ad-consent-notice]'),unit=host.querySelector('[data-jobpath-native]'),status=host.querySelector('[data-ad-status]');
  if(notice)notice.hidden=choice!==null||blocked;
  if(unit)unit.hidden=choice!=='allow'||blocked;
  if(status)status.textContent=blocked?'Advertising is off because your browser sends Global Privacy Control.':choice==='deny'?'Advertising is off for this browser.':'';
 }
}
export function startAdUnits(config){
 if(typeof document==='undefined'||typeof window==='undefined')return 0;
 if(adsterraReady(config)){
  syncNativePlacements();
  const ad=config.adsterra;
  const allowedHost=ad.websiteHost===CLOUDFLARE_ADSTERRA_HOST?CLOUDFLARE_ADSTERRA_HOST:ADSTERRA_HOST;
  const scriptUrl=ad.scriptUrl; // Exact pinned URL, validated by adsterraReady.
  if(window.location.hostname!==allowedHost||privacySignal()||readAdvertisingConsent()!=='allow')return 0;
  for(const unit of document.querySelectorAll('[data-jobpath-native]')){
   if(unit.id!==config.adsterra.containerId||unit.dataset.jobpathInitialized==='true')continue;
   if(document.querySelector('script[src="'+scriptUrl+'"]'))return 0;
   const script=document.createElement('script');
   // Reproduce the exact account-supplied native tag; do not use an iframe,
   // change its URL, add tracking parameters, or run it before consent.
   script.setAttribute('async','async');script.setAttribute('data-cfasync','false');
   script.src=scriptUrl;
   const status=unit.parentNode.querySelector('[data-ad-status]');
   script.addEventListener('error',()=>{if(status)status.textContent='Advertisement unavailable.'},{once:true});
   unit.dataset.jobpathInitialized='true';
   unit.parentNode.insertBefore(script,unit);
   return 1;
  }
  return 0;
 }
 if(!adSenseReady(config))return 0;
 let started=0;
 for(const unit of document.querySelectorAll('ins.adsbygoogle[data-jobpath-ad]')){
  if(unit.dataset.jobpathInitialized==='true')continue;
  try{
   (window.adsbygoogle=window.adsbygoogle||[]).push({});
   unit.dataset.jobpathInitialized='true';started++;
  }catch(error){
   // Failure never obstructs reading recruitment information.
   console.warn('Advertising request unavailable',error);
  }
 }
 return started;
}

export function openAdvertisingChoices(config){
 if(!adsterraReady(config)||typeof document==='undefined')return;
 let dialog=document.getElementById('jp-ad-choices');
 if(!dialog){
  dialog=document.createElement('dialog');dialog.id='jp-ad-choices';dialog.className='ad-choices-dialog';
  dialog.setAttribute('aria-labelledby','jp-ad-choices-title');
  dialog.innerHTML='<h2 id="jp-ad-choices-title">Advertising choices</h2><p>'+consentText+
   '</p><p><a href="/privacy-policy/">Read our privacy policy</a> and <a href="https://adsterra.com/privacy-policy-managed/" target="_blank" rel="noopener noreferrer">Adsterra privacy policy</a>.</p>'+consentButtons()+
   '<button type="button" class="btn btn-ghost btn-sm" data-ad-choices-close>Close</button>';
  document.body.append(dialog);
 }
 if(!dialog.open){if(typeof dialog.showModal==='function')dialog.showModal();else dialog.setAttribute('open','')}
 if(privacySignal()){
  const allow=dialog.querySelector('[data-ad-choice="allow"]');if(allow)allow.disabled=true;
 }
}
export function closeAdvertisingChoices(){
 const dialog=document.getElementById('jp-ad-choices');
 if(dialog?.close)dialog.close();else dialog?.removeAttribute('open');
}
export function chooseAdvertising(config,choice){
 if(!adsterraReady(config)||(choice==='allow'&&privacySignal())||!saveAdvertisingConsent(choice))return false;
 closeAdvertisingChoices();
 if(choice==='deny'&&document.querySelector('script[src="'+config.adsterra.scriptUrl+'"]')){
  // Reload removes the already-running third-party script and its timers.
  window.location.reload();return true;
 }
 // A first-time visitor may have no ad container until they opt in.
 if(choice==='allow'&&typeof document!=='undefined'&&!document.querySelector('[data-jobpath-native]')){
  window.location.reload();return true;
 }
 startAdUnits(config);return true;
}
