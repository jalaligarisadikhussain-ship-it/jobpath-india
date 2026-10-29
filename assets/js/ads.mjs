/** Approved, project-specific tags. Third-party native ads require explicit opt-in. */
const PUBLISHER=/^ca-pub-[0-9]{16}$/;
const SLOT=/^[0-9]{8,12}$/;
export const ADSTERRA_KEY='59088646af2816821f7d8b37df198113';
export const ADSTERRA_SCRIPT='https://bauval.org/21/'+ADSTERRA_KEY;
export const ADSTERRA_HOST='jobpath-india.netlify.app';
export const AD_CONSENT_KEY='jp_advertising_consent';
export const AD_CONSENT_VERSION='adsterra-2026-10-29';
const CONSENT_AGE=180*24*60*60*1000;

export function adsterraConfigured(config){
 const ad=config?.adsterra;
 return ad?.websiteId==='6159057'&&ad.adUnitId==='31978670'&&ad.format==='native'&&
  ad.key===ADSTERRA_KEY&&ad.scriptUrl===ADSTERRA_SCRIPT&&
  ad.containerId==='container-'+ADSTERRA_KEY&&ad.adultAds===false;
}
export function adsterraReady(config){
 return config?.enabled===true&&config.provider==='adsterra'&&adsterraConfigured(config)&&
  config.adsterra.siteStatus==='approved'&&config.adsterra.adUnitStatus==='active'&&
  config.consent?.required===true&&config.consent.version===AD_CONSENT_VERSION;
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
const consentText='Optional Adsterra advertising uses cookies and device/browser information, such as IP address and ad interactions. Allowing ads shares this information with Adsterra and its advertising partners. You can change your choice at any time.';
function consentButtons(){return '<div class="ad-consent-actions"><button type="button" class="btn btn-secondary" data-ad-choice="allow">Allow advertising</button><button type="button" class="btn btn-secondary" data-ad-choice="deny">Continue without ads</button></div>'}
export function renderAdPlacement(config,place='content'){
 if(place!=='content')return '';
 if(!advertisingReady(config)){
  return '<aside class="ad-placeholder" aria-label="Future advertising placement">Advertisement space · No ads are active</aside>';
 }
 if(adsterraReady(config))return '<aside class="ad-placement" aria-label="Advertisement" data-jobpath-native-placement>'+
  '<span class="ad-placement-label">Advertisement</span><div data-ad-consent-notice><p>'+consentText+
  ' <a href="/privacy-policy/">Privacy policy</a></p>'+consentButtons()+'</div>'+
  '<div id="'+config.adsterra.containerId+'" data-jobpath-native hidden></div>'+
  '<p class="tiny muted" data-ad-status role="status"></p><button type="button" class="btn btn-ghost btn-sm" data-ad-choices>Advertising choices</button></aside>';
 // User-provided identifiers must pass strict numeric allowlists; no HTML interpolation of untrusted strings.
 return '<aside class="ad-placement" aria-label="Advertisement">'+
  '<span class="ad-placement-label">Advertisement</span>'+
  '<ins class="adsbygoogle" style="display:block" data-jobpath-ad="content" data-ad-client="'+
  config.publisherId+'" data-ad-slot="'+config.slots.content+
  '" data-ad-format="auto" data-full-width-responsive="true"></ins></aside>';
}
function syncNativePlacements(){
 const choice=readAdvertisingConsent(),blocked=privacySignal();
 for(const host of document.querySelectorAll('[data-jobpath-native-placement]')){
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
  if(window.location.hostname!==ADSTERRA_HOST||privacySignal()||readAdvertisingConsent()!=='allow')return 0;
  for(const unit of document.querySelectorAll('[data-jobpath-native]')){
   if(unit.id!==config.adsterra.containerId||unit.dataset.jobpathInitialized==='true')continue;
   if(document.querySelector('script[src="'+ADSTERRA_SCRIPT+'"]'))return 0;
   const script=document.createElement('script');
   // Reproduce the exact account-supplied native tag; do not use an iframe,
   // change its URL, add tracking parameters, or run it before consent.
   script.setAttribute('async','async');script.setAttribute('data-cfasync','false');
   script.src=ADSTERRA_SCRIPT;
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
 if(choice==='deny'&&document.querySelector('script[src="'+ADSTERRA_SCRIPT+'"]')){
  // Reload removes the already-running third-party script and its timers.
  window.location.reload();return true;
 }
 startAdUnits(config);return true;
}
