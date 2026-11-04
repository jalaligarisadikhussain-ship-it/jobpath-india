'use strict';
// Deepavali tracking backend. The prize wheel remains DEMO. No payments or real awards.
const express=require('express'),{Pool}=require('pg'),crypto=require('node:crypto'),path=require('node:path');
const app=express();app.disable('x-powered-by');app.set('trust proxy',1);
const SITE=(process.env.FRONTEND_ORIGIN||'https://deepavali-dhamaka-spin-2026.onrender.com').replace(/\/$/,'');
const DB=process.env.DATABASE_URL?new Pool({connectionString:process.env.DATABASE_URL,ssl:process.env.DATABASE_URL.includes('localhost')?false:{rejectUnauthorized:false},max:4,connectionTimeoutMillis:8000}):null;
const ADMIN_PASSWORD=process.env.ADMIN_PASSWORD||'',ADMIN_SESSION_SECRET=process.env.ADMIN_SESSION_SECRET||'';
const signupLimit=new Map(),uploadLimit=new Map(),loginLimit=new Map();
const hash=s=>crypto.createHash('sha256').update(String(s)).digest('hex');
const token=()=>crypto.randomBytes(32).toString('base64url');
const fail=(res,n,msg)=>res.status(n).json({error:msg});
const asyncRoute=f=>(req,res,next)=>Promise.resolve(f(req,res,next)).catch(next);
const dbRequired=(req,res,next)=>DB?next():fail(res,503,'Tracking database not configured.');
function limit(map,key,n,ms){let now=Date.now(),v=map.get(key);if(!v||v.until<now){map.set(key,{count:1,until:now+ms});return true;}v.count++;return v.count<=n;}
app.use((req,res,next)=>{res.set('X-Content-Type-Options','nosniff');res.set('X-Frame-Options','DENY');res.set('Cache-Control','no-store');res.set('Referrer-Policy','strict-origin-when-cross-origin');if(req.secure)res.set('Strict-Transport-Security','max-age=31536000');next();});
app.use((req,res,next)=>{
 const origin=req.get('origin');
 if(origin===SITE){res.set('Access-Control-Allow-Origin',SITE);res.set('Vary','Origin');res.set('Access-Control-Allow-Methods','GET,POST,DELETE,OPTIONS');res.set('Access-Control-Allow-Headers','Content-Type,Authorization');}
 if(req.method==='OPTIONS')return res.sendStatus(origin&&! [SITE].includes(origin)?403:204);
 if(req.path.startsWith('/api/')&&origin&&origin!==SITE)return fail(res,403,'Origin not permitted.');
 next();
});
app.use(express.json({limit:'2mb',strict:true}));
let dbReady=false;
async function migrate(){
 if(!DB)return;
 await DB.query("CREATE TABLE IF NOT EXISTS dd_participants (id UUID PRIMARY KEY,nickname VARCHAR(60) NOT NULL,email VARCHAR(180) NOT NULL,token_hash CHAR(64) UNIQUE NOT NULL,referral_code VARCHAR(24) UNIQUE NOT NULL,referred_by UUID REFERENCES dd_participants(id) ON DELETE SET NULL,status VARCHAR(12) NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','verified','rejected')),consent_at TIMESTAMPTZ NOT NULL,verified_at TIMESTAMPTZ,created_at TIMESTAMPTZ NOT NULL DEFAULT NOW())");
 await DB.query('CREATE UNIQUE INDEX IF NOT EXISTS dd_unique_email ON dd_participants(LOWER(email))');
 await DB.query('CREATE INDEX IF NOT EXISTS dd_referrers ON dd_participants(referred_by,status)');
 await DB.query("CREATE TABLE IF NOT EXISTS dd_group_proofs (id UUID PRIMARY KEY,participant_id UUID NOT NULL REFERENCES dd_participants(id) ON DELETE CASCADE,group_name VARCHAR(80) NOT NULL,mime VARCHAR(20) NOT NULL,image_bytes BYTEA NOT NULL,status VARCHAR(12) NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','approved','rejected')),created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),reviewed_at TIMESTAMPTZ)");
 await DB.query('CREATE UNIQUE INDEX IF NOT EXISTS dd_proof_distinct_group ON dd_group_proofs(participant_id,LOWER(group_name))');
 dbReady=true;console.log('Database initialized');
}
migrate().catch(e=>{console.error('Database initialization unavailable:',e.message);});
app.get('/healthz',asyncRoute(async(req,res)=>{try{if(!DB)throw Error('missing DB');await DB.query('SELECT 1');res.json({status:'ok',database:'connected',prizes:'demo only'});}catch{res.status(503).json({status:'degraded',database:'not ready'});}}));
app.get('/api/config',(req,res)=>res.json({trackingReady:dbReady,prizesEnabled:false,spinMode:'demo',referrals:'manual review',groupProofs:'manual review'}));
async function visitor(req,res,next){
 const h=req.get('authorization')||'';
 if(!/^Bearer [A-Za-z0-9_-]{30,100}$/.test(h))return fail(res,401,'Registration session missing.');
 const r=await DB.query('SELECT * FROM dd_participants WHERE token_hash=$1',[hash(h.slice(7))]);
 if(!r.rows.length)return fail(res,401,'Registration session not found. Contact administrator.');
 req.participant=r.rows[0];next();
}
const registered=(req,res,next)=>asyncRoute(visitor)(req,res,next);
app.post('/api/enroll',dbRequired,asyncRoute(async(req,res)=>{
 if(!limit(signupLimit,req.ip,5,3600000))return fail(res,429,'Too many new registrations; try later.');
 const d=req.body||{},name=typeof d.nickname==='string'?d.nickname.trim():'',email=typeof d.email==='string'?d.email.trim().toLowerCase():'';
 if(d.consent!==true)return fail(res,400,'Consent required to process your registration.');
 if(name.length<2||name.length>60)return fail(res,400,'Display name must be 2–60 characters.');
 if(email.length>180||!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))return fail(res,400,'Valid contact email required.');
 let referrer=null;
 if(typeof d.referralCode==='string'&&/^SPIN-[0-9A-F]{16}$/i.test(d.referralCode)){
  const r=await DB.query('SELECT id,email FROM dd_participants WHERE referral_code=$1',[d.referralCode.toUpperCase()]);
  if(r.rows.length){if(r.rows[0].email.toLowerCase()===email)return fail(res,400,'Self referral is not allowed.');referrer=r.rows[0].id;}
 }
 const id=crypto.randomUUID(),secret=token(),code='SPIN-'+crypto.randomBytes(8).toString('hex').toUpperCase();
 try{await DB.query('INSERT INTO dd_participants(id,nickname,email,token_hash,referral_code,referred_by,consent_at) VALUES($1,$2,$3,$4,$5,$6,NOW())',[id,name,email,hash(secret),code,referrer]);}
 catch(e){if(e.code==='23505')return fail(res,409,'Email already registered. Use the original browser or contact the organizer.');throw e;}
 res.status(201).json({token:secret,member:{id,nickname:name,email,referralCode:code,status:'pending'},notice:'Registration pending. This does not verify unique identity or activate a prize.'});
}));
app.get('/api/me',dbRequired,registered,asyncRoute(async(req,res)=>{
 const p=req.participant;
 const counts=await DB.query("SELECT (SELECT COUNT(*)::INT FROM dd_participants WHERE referred_by=$1 AND status='verified') verified_referrals,(SELECT COUNT(*)::INT FROM dd_participants WHERE referred_by=$1 AND status='pending') pending_referrals,(SELECT COUNT(*)::INT FROM dd_group_proofs WHERE participant_id=$1 AND status='approved') approved_groups,(SELECT COUNT(*)::INT FROM dd_group_proofs WHERE participant_id=$1 AND status='pending') pending_groups",[p.id]);
 const proofs=await DB.query('SELECT id,group_name,status,created_at FROM dd_group_proofs WHERE participant_id=$1 ORDER BY created_at DESC',[p.id]);
 res.json({member:{id:p.id,nickname:p.nickname,email:p.email,referralCode:p.referral_code,status:p.status},...counts.rows[0],proofs:proofs.rows.map(q=>({id:q.id,groupName:q.group_name,status:q.status})),eligibleForPrize:false,prizesEnabled:false});
}));
function validateImage(data){
 if(typeof data!=='string'||data.length>1300000)return null;
 const m=/^data:image\/(jpeg|png|webp);base64,([A-Za-z0-9+/=]+)$/.exec(data);if(!m)return null;
 const b=Buffer.from(m[2],'base64');if(b.length<100||b.length>900000)return null;
 const jpeg=b[0]===255&&b[1]===216&&b[2]===255,png=b.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10])),webp=b.subarray(0,4).toString()==='RIFF'&&b.subarray(8,12).toString()==='WEBP';
 if(!(m[1]==='jpeg'&&jpeg||m[1]==='png'&&png||m[1]==='webp'&&webp))return null;
 return{mime:'image/'+m[1],bytes:b};
}
app.post('/api/proofs',dbRequired,registered,asyncRoute(async(req,res)=>{
 if(!limit(uploadLimit,req.participant.id,10,3600000))return fail(res,429,'Too many proof submissions. Try later.');
 const d=req.body||{},label=typeof d.groupName==='string'?d.groupName.trim():'',picture=validateImage(d.imageData);
 if(d.consent!==true)return fail(res,400,'Consent to private screenshot review required.');
 if(label.length<3||label.length>80)return fail(res,400,'Group label must be 3–80 characters.');
 if(!picture)return fail(res,400,'Valid JPEG/PNG/WebP image below 900 KB required.');
 const c=await DB.connect();try{
  await c.query('BEGIN');await c.query('SELECT id FROM dd_participants WHERE id=$1 FOR UPDATE',[req.participant.id]);
  const n=await c.query('SELECT COUNT(*)::INT AS total FROM dd_group_proofs WHERE participant_id=$1',[req.participant.id]);
  if(n.rows[0].total>=5){await c.query('ROLLBACK');return fail(res,409,'Five group proofs already submitted.');}
  const id=crypto.randomUUID();
  await c.query('INSERT INTO dd_group_proofs(id,participant_id,group_name,mime,image_bytes) VALUES($1,$2,$3,$4,$5)',[id,req.participant.id,label,picture.mime,picture.bytes]);
  await c.query('COMMIT');res.status(201).json({id,status:'pending',notice:'Submitted for private manual review. WhatsApp delivery is not automatically verified.'});
 }catch(e){await c.query('ROLLBACK');if(e.code==='23505')return fail(res,409,'Group already submitted.');throw e;}finally{c.release();}
}));
app.delete('/api/me',dbRequired,registered,asyncRoute(async(req,res)=>{await DB.query('DELETE FROM dd_participants WHERE id=$1',[req.participant.id]);res.json({deleted:true});}));
function signature(exp,nonce){return crypto.createHmac('sha256',ADMIN_SESSION_SECRET).update(exp+'.'+nonce).digest('base64url');}
function adminSession(req){
 const m=/(?:^|;\s*)dd_admin=([^;]+)/.exec(req.get('cookie')||'');
 if(!m||ADMIN_SESSION_SECRET.length<32)return false;
 const parts=m[1].split('.');if(parts.length!==3||!/^\d{10,14}$/.test(parts[0])||Number(parts[0])<Date.now())return false;
 const a=Buffer.from(signature(parts[0],parts[1])),b=Buffer.from(parts[2]);return a.length===b.length&&crypto.timingSafeEqual(a,b);
}
const adminOnly=(req,res,next)=>adminSession(req)?next():fail(res,401,'Administrator login required.');
function adminOrigin(req,res,next){
 const origin=req.get('origin');
 if(!origin||!req.get('host')||origin!=='https://'+req.get('host'))return fail(res,403,'Invalid admin action origin.');
 next();
}
const adminCsp=(req,res,next)=>{res.set('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'none'; frame-ancestors 'none'");next();};
app.get('/admin',adminCsp,(req,res)=>res.sendFile(path.join(__dirname,'public','admin.html')));
app.get('/admin/app.js',adminCsp,(req,res)=>res.sendFile(path.join(__dirname,'public','admin.js')));
app.get('/admin/api/session',(req,res)=>res.json({authenticated:adminSession(req),prizesEnabled:false}));
app.post('/admin/api/login',adminOrigin,(req,res)=>{
 if(!limit(loginLimit,req.ip,8,900000))return fail(res,429,'Too many login attempts. Retry in 15 minutes.');
 if(ADMIN_PASSWORD.length<20||ADMIN_SESSION_SECRET.length<32)return fail(res,503,'Admin secrets not configured.');
 const p=typeof req.body?.password==='string'?req.body.password:'';
 const a=crypto.createHash('sha256').update(p).digest(),b=crypto.createHash('sha256').update(ADMIN_PASSWORD).digest();
 if(!crypto.timingSafeEqual(a,b))return fail(res,401,'Invalid password.');
 const exp=String(Date.now()+8*3600000),nonce=crypto.randomBytes(16).toString('base64url');
 res.cookie('dd_admin',exp+'.'+nonce+'.'+signature(exp,nonce),{secure:true,httpOnly:true,sameSite:'strict',path:'/admin',maxAge:8*3600000});res.json({authenticated:true});
});
app.post('/admin/api/logout',adminOrigin,(req,res)=>{res.clearCookie('dd_admin',{path:'/admin',secure:true,sameSite:'strict'});res.json({authenticated:false});});
app.get('/admin/api/participants',dbRequired,adminOnly,asyncRoute(async(req,res)=>{
 const r=await DB.query("SELECT p.id,p.nickname,p.email,p.referral_code,p.referred_by,p.status,p.created_at,(SELECT COUNT(*)::INT FROM dd_participants q WHERE q.referred_by=p.id AND q.status='verified') verified_referrals,(SELECT COUNT(*)::INT FROM dd_participants q WHERE q.referred_by=p.id AND q.status='pending') pending_referrals,(SELECT COUNT(*)::INT FROM dd_group_proofs g WHERE g.participant_id=p.id AND g.status='approved') approved_groups FROM dd_participants p ORDER BY p.created_at DESC LIMIT 250");
 const t=await DB.query("SELECT (SELECT COUNT(*)::INT FROM dd_participants) total_members,(SELECT COUNT(*)::INT FROM dd_participants WHERE status='verified') verified_members,(SELECT COUNT(*)::INT FROM dd_group_proofs WHERE status='pending') pending_proofs");
 res.json({participants:r.rows,totals:t.rows[0],prizesEnabled:false});
}));
app.get('/admin/api/proofs',dbRequired,adminOnly,asyncRoute(async(req,res)=>{
 const r=await DB.query("SELECT g.id,g.participant_id,g.group_name,g.status,g.created_at,p.nickname,p.email FROM dd_group_proofs g JOIN dd_participants p ON p.id=g.participant_id ORDER BY CASE WHEN g.status='pending' THEN 0 ELSE 1 END,g.created_at DESC LIMIT 250");
 res.json({proofs:r.rows});
}));
app.get('/admin/api/proofs/:id/image',dbRequired,adminOnly,asyncRoute(async(req,res)=>{
 if(!/^[a-f0-9-]{36}$/i.test(req.params.id))return fail(res,400,'Invalid ID');
 const r=await DB.query('SELECT mime,image_bytes FROM dd_group_proofs WHERE id=$1',[req.params.id]);
 if(!r.rows.length)return fail(res,404,'Proof not found.');
 res.set('Content-Type',r.rows[0].mime);res.set('Content-Disposition','inline');res.send(r.rows[0].image_bytes);
}));
app.post('/admin/api/participants/:id/status',dbRequired,adminOnly,adminOrigin,asyncRoute(async(req,res)=>{
 const status=req.body?.status;if(!['pending','verified','rejected'].includes(status))return fail(res,400,'Invalid status');
 const r=await DB.query("UPDATE dd_participants SET status=$1,verified_at=CASE WHEN $1='verified' THEN NOW() ELSE NULL END WHERE id=$2 RETURNING id,status",[status,req.params.id]);
 if(!r.rows.length)return fail(res,404,'Member not found');res.json({updated:r.rows[0]});
}));
app.post('/admin/api/proofs/:id/status',dbRequired,adminOnly,adminOrigin,asyncRoute(async(req,res)=>{
 const status=req.body?.status;if(!['pending','approved','rejected'].includes(status))return fail(res,400,'Invalid status');
 const r=await DB.query("UPDATE dd_group_proofs SET status=$1,reviewed_at=CASE WHEN $1='pending' THEN NULL ELSE NOW() END WHERE id=$2 RETURNING id,status",[status,req.params.id]);
 if(!r.rows.length)return fail(res,404,'Proof not found');res.json({updated:r.rows[0]});
}));
app.delete('/admin/api/proofs/:id',dbRequired,adminOnly,adminOrigin,asyncRoute(async(req,res)=>{
 const r=await DB.query('DELETE FROM dd_group_proofs WHERE id=$1 RETURNING id',[req.params.id]);
 if(!r.rows.length)return fail(res,404,'Proof not found');res.json({deleted:true});
}));
app.use((err,req,res,next)=>{console.error('Request error:',err.message);if(!res.headersSent)fail(res,err.type==='entity.too.large'?413:500,err.type==='entity.too.large'?'Image too large. Compress it.':'Server error. Please retry.');});
app.listen(Number(process.env.PORT)||10000,'0.0.0.0',()=>console.log('Deepavali tracking preview API started'));
