'use strict';
const $=id=>document.getElementById(id),K='deepavali_anon_proof_token_v1';
const fragment=new URLSearchParams(location.hash.replace(/^#/,'')),incoming=fragment.get('key')||'';
if(/^[A-Za-z0-9_-]{30,100}$/.test(incoming))try{localStorage.setItem(K,incoming);}catch{}
if(location.hash)history.replaceState(null,'',location.pathname+location.search);
const token=()=>{try{return localStorage.getItem(K)||'';}catch{return '';}};
function status(s){$('state').textContent=s;}
async function api(route,options={}){
 const r=await fetch('/api/anon/'+route,{cache:'no-store',...options,headers:{'Content-Type':'application/json','Authorization':'Bearer '+token(),...(options.headers||{})}});
 const d=await r.json();if(!r.ok)throw Error(d.error||'Request failed');return d;
}
async function refresh(){
 if(!token()){status('Open the Wheel, finish a spin, and tap Submit Group Proof to open this private page. No registration is required.');$('upload').disabled=true;return;}
 try{
  const {overview}=await api('me');
  status('Connected. Only you and the organizer can review your submitted screenshot statuses.');
  const approved=overview.approvedGroups,pending=overview.groupProofs.filter(p=>p.status==='pending').length;
  $('counts').textContent=approved+' / 5 screenshots approved by organizer · '+pending+' pending. Approval does not prove WhatsApp delivery.';
  const root=$('proofs');root.replaceChildren();
  for(const item of overview.groupProofs){const row=document.createElement('div');row.className='proof-status';row.textContent=item.groupLabel+' — '+item.status;root.append(row);}
  if(!overview.groupProofs.length)root.textContent='No screenshots yet.';
  $('upload').disabled=overview.groupProofs.length>=5;
 }catch(e){status(e.message);$('upload').disabled=true;}
}
function shrink(file){
 return new Promise((resolve,reject)=>{
  if(!file||!/^image\/(png|jpeg|webp)$/.test(file.type)||file.size>12000000)return reject(Error('Choose a JPEG/PNG/WebP screenshot under 12 MB.'));
  const url=URL.createObjectURL(file),im=new Image();
  im.onload=()=>{
   try{
    const factor=Math.min(1,1200/Math.max(im.width,im.height)),canvas=document.createElement('canvas');
    canvas.width=Math.max(1,Math.floor(im.width*factor));canvas.height=Math.max(1,Math.floor(im.height*factor));
    canvas.getContext('2d').drawImage(im,0,0,canvas.width,canvas.height);
    const result=canvas.toDataURL('image/jpeg',0.68);
    URL.revokeObjectURL(url);
    if(result.length>1200000)reject(Error('Crop or compress screenshot below 900 KB.'));else resolve(result);
   }catch(e){URL.revokeObjectURL(url);reject(e);}
  };
  im.onerror=()=>{URL.revokeObjectURL(url);reject(Error('Image could not be opened.'));};im.src=url;
 });
}
$('proofForm').addEventListener('submit',async e=>{
 e.preventDefault();$('upload').disabled=true;status('Preparing screenshot for private review…');
 try{
  const imageData=await shrink($('image').files[0]);
  const data=await api('proof',{method:'POST',body:JSON.stringify({groupLabel:$('group').value,imageData,consent:$('consent').checked})});
  $('proofForm').reset();status(data.note);await refresh();
 }catch(err){status(err.message);$('upload').disabled=false;}
});
$('remove').addEventListener('click',async()=>{
 if(!confirm('Permanently delete your anonymous tracking records and submitted screenshots?'))return;
 try{await api('me',{method:'DELETE'});localStorage.removeItem(K);status('Deleted. New visitors may get a fresh browser token on the wheel.');$('proofs').replaceChildren();$('counts').textContent='Deleted';$('upload').disabled=true;}catch(e){status(e.message);}
});
refresh();
