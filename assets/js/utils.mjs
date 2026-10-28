export const ALLOWED_STATUSES=['open','upcoming','closed','unverified'];
export const QUALIFICATIONS=['10th Pass','12th Pass','ITI','Diploma','Any Degree','B.Tech / Engineering','Postgraduate','Other'];
export function safeUrl(value){try{const u=new URL(value);return u.protocol==='https:'?u.href:null}catch{return null}}
export function escapeHTML(value){return String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
export function isISODate(value){return typeof value==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(value)&&!Number.isNaN(Date.parse(value+'T00:00:00Z'))&&new Date(value+'T00:00:00Z').toISOString().slice(0,10)===value}
export function daysUntil(date,now=new Date()){if(!isISODate(date))return null;const d=Date.parse(date+'T00:00:00Z');const today=Date.UTC(now.getFullYear(),now.getMonth(),now.getDate());return Math.round((d-today)/86400000)}
export function effectiveStatus(job,now=new Date()){if(!job||!job.verified||job.status==='unverified')return 'unverified';const until=daysUntil(job.lastDate,now);if(until!==null&&until<0)return 'closed';if(isISODate(job.startDate)&&daysUntil(job.startDate,now)>0)return 'upcoming';return job.status==='closed'?'closed':'open'}
// For demo records, expose simulated dates without suggesting an official opening.
export function sampleStatus(job,now=new Date()){if(!job.isDemo)return effectiveStatus(job,now);const remain=daysUntil(job.lastDate,now);return remain!==null&&remain<0?'closed':daysUntil(job.startDate,now)>0?'upcoming':'open'}
export function filterJobs(items,filters={},now=new Date()){
 let out=items.filter(job=>{
 const q=String(filters.q||'').trim().toLowerCase(); const search=[job.title,job.organization,job.department,job.state,job.category,job.qualification].join(' ').toLowerCase();
 if(q&&!search.includes(q))return false;
 for(const key of ['state','type','qualification','department','organization','category'])if(filters[key]&&String(job[key]).toLowerCase()!==String(filters[key]).toLowerCase())return false;
 const st=job.isDemo?sampleStatus(job,now):effectiveStatus(job,now);
 if(filters.status&&st!==filters.status)return false;
 if(filters.deadline==='7'&&!(daysUntil(job.lastDate,now)>=0&&daysUntil(job.lastDate,now)<=7))return false;
 if(filters.deadline==='30'&&!(daysUntil(job.lastDate,now)>=0&&daysUntil(job.lastDate,now)<=30))return false;
 if(filters.deadline==='future'&&!(daysUntil(job.lastDate,now)>=0))return false;
 return true;
 });
 return out.sort((a,b)=>{
 switch(filters.sort){case 'deadline':return (a.lastDate||'9999').localeCompare(b.lastDate||'9999');case 'title':return a.title.localeCompare(b.title);case 'organization':return a.organization.localeCompare(b.organization);default:return (b.publishedDate||'').localeCompare(a.publishedDate||'')}
 });
}
export function validateJobs(jobs){const errors=[];if(!Array.isArray(jobs))return ['jobs.json must contain a JSON array'];const ids=new Set();jobs.forEach((j,i)=>{const p=`Record ${i+1}`;for(const key of ['id','title','organization','type','state','qualification','department','category','status','sourceOrganization'])if(!j[key]||typeof j[key]!=='string')errors.push(`${p}: missing ${key}`);if(ids.has(j.id))errors.push(`${p}: duplicate ID ${j.id}`);ids.add(j.id);if(!ALLOWED_STATUSES.includes(j.status))errors.push(`${p}: invalid status`);for(const k of ['startDate','lastDate','publishedDate','lastVerifiedDate'])if(j[k]&&!isISODate(j[k]))errors.push(`${p}: bad ${k}`);if(j.verified&&!j.isDemo&&(!safeUrl(j.notificationUrl)||!safeUrl(j.applicationUrl)||!isISODate(j.lastVerifiedDate)))errors.push(`${p}: verified jobs require valid official HTTPS notification/application URLs and verification date`);if(!j.isDemo&&!j.verified&&j.status!=='unverified')errors.push(`${p}: unverified records cannot be marked open`);if(j.isDemo&&(j.notificationUrl||j.applicationUrl))errors.push(`${p}: demo jobs cannot contain application URLs`);});return errors}

// Public pages never display invented or unverified jobs as live vacancies.
export function publicJobs(items,includeDemos=false){return items.filter(j=>(j.verified===true&&j.isDemo!==true&&j.status!=='unverified')||(includeDemos&&j.isDemo===true))}
