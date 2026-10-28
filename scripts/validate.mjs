import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {validateJobs,safeUrl} from '../assets/js/utils.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const data=JSON.parse(fs.readFileSync(path.join(root,'data/jobs.json')));
const sources=JSON.parse(fs.readFileSync(path.join(root,'data/sources.json')));
const issues=validateJobs(data);
for (const source of sources){if(source.url&&!safeUrl(source.url))issues.push(`Invalid source URL for ${source.name}`)}
for(const p of Object.keys(JSON.parse(fs.readFileSync(path.join(root,'data/pages.json'))))){const page=JSON.parse(fs.readFileSync(path.join(root,'data/pages.json')))[p];if(!fs.existsSync(path.join(root,page.path,'index.html')))issues.push(`Missing page: ${p}`)}
if(issues.length){console.error(issues.join('\n'));process.exitCode=1}else console.log(`PASS: ${data.length} valid recruitment/example records, ${sources.length} directory sources and all static page files present`);
