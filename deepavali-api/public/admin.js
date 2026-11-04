'use strict';
const $=id=>document.getElementById(id);
const feedback=msg=>{$('feedback').textContent=msg;};
async function call(route,options={}){
 const res=await fetch('/admin/api/'+route,{credentials:'same-origin',cache:'no-store',...options,headers:{'Content-Type':'application/json',...(options.headers||{})}});
 const json=await res.json();
 if(!res.ok)throw Error(json.error||'Request failed');
 return json;
}
const make=(tag,text,className='')=>{const n=document.createElement(tag);if(text!==undefined)n.textContent=String(text);if(className)n.className=className;return n;};
const action=(title,fn,kind)=>{const b=make('button',title,kind||'');b.type='button';b.onclick=async()=>{b.disabled=true;try{await fn();}catch(e){feedback(e.message);}finally{b.disabled=false;}};return b;};
function summary(name,n){const el=make('div',null,'stat');el.append(make('strong',n),make('span',name));return el;}
function kv(el,key,val){el.append(make('div',key+': '+String(val),'meta'));}
async function changeStatus(kind,id,status){
 if(status==='verified'&&!confirm('Only confirm after independently checking this is a genuine distinct participant. Email field alone is not verified. Continue?'))return;
 if(status==='approved'&&!confirm('Screenshot alone cannot prove a WhatsApp group delivery. Have you reviewed independent evidence?'))return;
 const route=kind==='participant'?'participants/'+id+'/status':'proofs/'+id+'/status';
 await call(route,{method:'POST',body:JSON.stringify({status})});
 feedback('Updated '+kind+' status to '+status+'.');
 await load();
}
function renderMember(p){
 const card=make('article',null,'item'),head=make('h3',p.nickname+' · '+p.status);
 card.append(head);
 kv(card,'Email (not independently confirmed)',p.email);
 kv(card,'Referral code',p.referral_code);
 kv(card,'Referred by',p.referred_by||'Direct');
 kv(card,'Verified / pending referrals',p.verified_referrals+' / '+p.pending_referrals);
 kv(card,'Approved group proofs',p.approved_groups);
 const controls=make('div',null,'controls');
 controls.append(action('Verify member',()=>changeStatus('participant',p.id,'verified'),'confirm'),
 action('Reject',()=>changeStatus('participant',p.id,'rejected'),'reject'),
 action('Mark pending',()=>changeStatus('participant',p.id,'pending')));
 card.append(controls);return card;
}
function renderProof(p){
 const card=make('article',null,'item');card.append(make('h3',p.group_name+' · '+p.status));
 kv(card,'Submitted by',p.nickname+' ('+p.email+')');
 kv(card,'Submitted',new Date(p.created_at).toLocaleString());
 const controls=make('div',null,'controls');
 const link=make('a','View private proof image');link.href='/admin/api/proofs/'+encodeURIComponent(p.id)+'/image';link.target='_blank';link.rel='noopener noreferrer';controls.append(link,
 action('Approve',()=>changeStatus('proof',p.id,'approved'),'confirm'),
 action('Reject',()=>changeStatus('proof',p.id,'rejected'),'reject'),
 action('Reset to pending',()=>changeStatus('proof',p.id,'pending')));
 controls.append(action('Delete image',async()=>{
   if(!confirm('Permanently delete this screenshot and proof record?'))return;
   await call('proofs/'+p.id,{method:'DELETE'});feedback('Private image deleted.');await load();
 },'reject'));
 card.append(controls);return card;
}

function renderAnonPlayer(p){
 const card=make('article',null,'item');card.append(make('h3','Anonymous browser '+p.referral_code));
 kv(card,'Unique browser plays from its link (NOT unique humans)',p.unique_browser_plays+' / 20');
 kv(card,'Group screenshots reviewed approved',p.approved_groups+' / 5');
 kv(card,'Played spin',p.engaged_at?'Yes':'Not yet');kv(card,'Referred from',p.referred_by||'Direct');
 return card;
}
async function changeAnonProof(id,status){
 if(status==='approved'&&!confirm('The screenshot is redacted and reviewable. Approval is NOT WhatsApp delivery verification. Approve?'))return;
 await call('anon-proofs/'+id+'/status',{method:'POST',body:JSON.stringify({status})});
 feedback('Anonymous proof review: '+status);await load();
}
function renderAnonProof(p){
 const card=make('article',null,'item');card.append(make('h3',p.group_label+' — '+p.status));
 kv(card,'Browser referral code',p.referral_code);kv(card,'Uploaded',new Date(p.created_at).toLocaleString());
 const controls=make('div',null,'controls'),link=make('a','View private screenshot');
 link.href='/admin/api/anon-proofs/'+encodeURIComponent(p.id)+'/image';link.target='_blank';link.rel='noopener noreferrer';
 controls.append(link,action('Approve review',()=>changeAnonProof(p.id,'approved'),'confirm'),action('Reject',()=>changeAnonProof(p.id,'rejected'),'reject'),action('Set pending',()=>changeAnonProof(p.id,'pending')));
 controls.append(action('Delete screenshot',async()=>{
  if(!confirm('Permanently delete this private screenshot?'))return;
  await call('anon-proofs/'+p.id,{method:'DELETE'});await load();
 },'reject'));
 card.append(controls);return card;
}
async function load(){
 const [m,p,anon,anonProof]=await Promise.all([call('participants'),call('proofs'),call('anon-players'),call('anon-proofs')]);
 $('stats').replaceChildren(summary('Registered',m.totals.total_members),summary('Manually verified members',m.totals.verified_members),summary('Pending proof reviews',m.totals.pending_proofs));
 $('members').replaceChildren(...m.participants.map(renderMember));
 if(!m.participants.length)$('members').append(make('p','No participant registrations yet.'));
 $('proofs').replaceChildren(...p.proofs.map(renderProof));
 if(!p.proofs.length)$('proofs').append(make('p','No WhatsApp proof submissions yet.'));
 $('anonStats').replaceChildren(summary('Anonymous browsers',anon.totals.browsers),summary('Browsers that spun',anon.totals.players),summary('Pending group screenshots',anon.totals.pending_group_proofs));
 $('anonPlayers').replaceChildren(...anon.players.map(renderAnonPlayer));
 if(!anon.players.length)$('anonPlayers').append(make('p','No anonymous browser sessions yet.'));
 $('anonProofs').replaceChildren(...anonProof.proofs.map(renderAnonProof));
 if(!anonProof.proofs.length)$('anonProofs').append(make('p','No anonymous group screenshots submitted.'));
}
async function updateSession(){
 const s=await call('session');
 $('loginCard').hidden=s.authenticated;$('adminArea').hidden=!s.authenticated;$('logout').hidden=!s.authenticated;
 if(s.authenticated)await load();
}
$('loginForm').addEventListener('submit',async e=>{e.preventDefault();try{
 await call('login',{method:'POST',body:JSON.stringify({password:$('password').value})});$('password').value='';
 feedback('Signed in.');await updateSession();
}catch(err){feedback(err.message);}});
$('logout').addEventListener('click',async()=>{try{await call('logout',{method:'POST',body:'{}'});feedback('Signed out.');await updateSession();}catch(e){feedback(e.message);}});
$('refresh').addEventListener('click',()=>load().catch(e=>feedback(e.message)));
updateSession().catch(e=>feedback(e.message));
