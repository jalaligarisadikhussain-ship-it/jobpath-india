/** Minimal consent-aware entry point. Activated only after real publisher setup. */
const PUBLISHER=/^ca-pub-[0-9]{16}$/;
const SLOT=/^[0-9]{8,12}$/;
export function adSenseReady(config){
 return config?.enabled===true&&config.provider==='adsense'&&
   typeof config.publisherId==='string'&&PUBLISHER.test(config.publisherId)&&
   typeof config.slots?.content==='string'&&SLOT.test(config.slots.content);
}
export function renderAdPlacement(config,place='content'){
 if(place!=='content')return '';
 if(!adSenseReady(config)){
  return '<aside class="ad-placeholder" aria-label="Future advertising placement">Advertisement space · No ads are active</aside>';
 }
 // User-provided identifiers must pass strict numeric allowlists; no HTML interpolation of untrusted strings.
 return '<aside class="ad-placement" aria-label="Advertisement">'+
  '<span class="ad-placement-label">Advertisement</span>'+
  '<ins class="adsbygoogle" style="display:block" data-jobpath-ad="content" data-ad-client="'+
  config.publisherId+'" data-ad-slot="'+config.slots.content+
  '" data-ad-format="auto" data-full-width-responsive="true"></ins></aside>';
}
export function startAdUnits(config){
 if(!adSenseReady(config)||typeof document==='undefined'||typeof window==='undefined')return 0;
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
