'use strict';
const API='https://deepavali-dhamaka-tracking-api.onrender.com';
const TOKEN_KEY='deepavali_tracking_participant_token_v1';
const $=id=>document.getElementById(id);
let me=null;
function feedback(t){$('feedback').textContent=t;}
function savedToken(){try{return localStorage.getItem(TOKEN_KEY)||'';}catch{return '';}}
function cleanRef(){const params=new URL(location.href).searchParams;const x=params.get('ref')||'';return /^SPIN-[A-F0-9]{16}$/i.test(x)?x.toUpperCase():'';}
async function api(route,options={}){
 const h={'Content-Type':'application/json',...(options.headers||{})};
 if(savedToken())h.Authorization='Bearer '+savedToken();
 let r;
 try{r=await fetch(API+'/api/'+route,{cache:'no-store',...options,headers:h});}
 catch{throw Error('Tracking API unavailable right now. Please try later.');}
 let obj;try{obj=await r.json();}catch{throw Error('Tracking backend returned an invalid response.');}
 if(!r.ok)throw Error(obj.error||'Tracking request failed');
 return obj;
}
function setAccount(registered){
 $('enrollPanel').hidden=registered;$('accountPanel').hidden=!registered;$('proofPanel').hidden=!registered;$('privacyPanel').hidden=!registered;
}
function displayRecord(d){
 me=d;setAccount(true);
 $('registrationStatus').textContent='Your registration: '+d.member.status.toUpperCase()+'. Email identity is not automatically verified.';
 $('verifiedReferrals').textContent=d.verified_referrals+' / 20';
 $('pendingReferrals').textContent=String(d.pending_referrals);
 $('approvedGroups').textContent=d.approved_groups+' / 5';
 $('pendingGroups').textContent=String(d.pending_groups);
 $('trackingLink').value=new URL('./?ref='+encodeURIComponent(d.member.referralCode),location.href).href;
 const host=$('proofHistory');host.replaceChildren();
 for(const p of d.proofs){const e=document.createElement('div');e.className='proof';const strong=document.createElement('strong');strong.textContent=p.groupName+' — '+p.status;e.append(strong);host.append(e);}
 if(!d.proofs.length)host.textContent='No screenshots submitted yet.';
 $('proofButton').disabled=d.proofs.length>=5;
}
async function reloadMember(){
 if(!savedToken()){setAccount(false);return;}
 try{displayRecord(await api('me'));}
 catch(e){feedback(e.message);setAccount(false);}
}
async function connect(){
 try{
  const c=await api('config');$('connectionStatus').textContent=c.trackingReady?'Tracking backend connected. Genuine verification requires admin review. No real prizes.':'Tracking backend is being prepared. Registration will be available only after the database is connected.';
  $('enrollButton').disabled=!c.trackingReady;
  await reloadMember();
 }catch(e){$('connectionStatus').textContent=e.message;$('enrollButton').disabled=true;setAccount(false);}
}
$('enrollForm').addEventListener('submit',async e=>{
 e.preventDefault();$('enrollButton').disabled=true;feedback('Registering securely…');
 try{
  const d=await api('enroll',{method:'POST',body:JSON.stringify({nickname:$('nickname').value,email:$('email').value,referralCode:cleanRef(),consent:$('enrollConsent').checked})});
  localStorage.setItem(TOKEN_KEY,d.token);
  feedback('Registration recorded. Verification pending, no real gift is active.');
  await reloadMember();
 }catch(err){feedback(err.message);}finally{$('enrollButton').disabled=false;}
});
function shrinkPhoto(file){
 return new Promise((resolve,reject)=>{
  if(!file||!/^image\/(png|jpeg|webp)$/.test(file.type))return reject(Error('Choose a JPEG, PNG or WebP screenshot.'));
  if(file.size>12000000)return reject(Error('Image exceeds 12 MB.'));
  const img=new Image(),u=URL.createObjectURL(file);
  img.onload=()=>{try{
    const f=Math.min(1,1200/Math.max(img.width,img.height));
    const c=document.createElement('canvas');c.width=Math.round(img.width*f);c.height=Math.round(img.height*f);
    c.getContext('2d').drawImage(img,0,0,c.width,c.height);
    const encoded=c.toDataURL('image/jpeg',0.7);URL.revokeObjectURL(u);
    if(encoded.length>1200000)reject(Error('Image too large after compression. Crop or blur sensitive details first.'));else resolve(encoded);
   }catch(e){URL.revokeObjectURL(u);reject(e);}};
  img.onerror=()=>{URL.revokeObjectURL(u);reject(Error('Could not read screenshot.'));};img.src=u;
 });
}
$('proofForm').addEventListener('submit',async e=>{
 e.preventDefault();$('proofButton').disabled=true;feedback('Preparing private screenshot…');
 try{
  const imageData=await shrinkPhoto($('proofImage').files[0]);
  const d=await api('proofs',{method:'POST',body:JSON.stringify({groupName:$('groupName').value,imageData,consent:$('proofConsent').checked})});
  feedback(d.notice);$('proofForm').reset();await reloadMember();
 }catch(err){feedback(err.message);}finally{if(!me||me.proofs.length<5)$('proofButton').disabled=false;}
});
$('copyLink').addEventListener('click',async()=>{try{await navigator.clipboard.writeText($('trackingLink').value);feedback('Referral invitation copied.');}catch{feedback('Select and copy the link manually.');}});
$('shareWhatsApp').addEventListener('click',()=>{
 const msg=$('trackingLink').value+'\n\n🪔 Deepavali Dhamaka: optional referral tracking preview. No real prizes or discount coupons are active. Join only if interested.';
 window.open('https://wa.me/?text='+encodeURIComponent(msg),'_blank','noopener,noreferrer');
});
$('deleteAccount').addEventListener('click',async()=>{
 if(!confirm('Permanently delete your registered email, referral account, and all uploaded proofs? This cannot be undone.'))return;
 try{await api('me',{method:'DELETE'});localStorage.removeItem(TOKEN_KEY);me=null;setAccount(false);feedback('Your registration and private proof images were deleted.');}catch(e){feedback(e.message);}
});
if(cleanRef()){$('inviterNote').hidden=false;$('inviterNote').textContent='You followed referral '+cleanRef()+'. It counts only if the organizer independently verifies your registration.';}
connect();
