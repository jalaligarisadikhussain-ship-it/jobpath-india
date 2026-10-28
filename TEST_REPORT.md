# JOBPATH INDIA V1 — Quality Assurance Report

**Generated:** 2026-10-28 (build date)

## Checks performed

| Area | Result | Evidence |
|---|---|---|
| JSON data validation and unique IDs | PASS | `npm run validate` — 10 sample records, all file routes present |
| Core unit testing | PASS | `npm test` — 10/10 passing |
| Deadline calculations and automatic expiration | PASS | Unit tests include today, future and past deadlines |
| Search, combined filters, sort and clear logic | PASS (logic only) | Unit tests cover keyword, state, qualification, organization, department, category, status, date and sort |
| HTML escaping and URL protocol check | PASS | Unit tests for malicious HTML and `javascript:`/HTTP URLs |
| SEO metadata and file references | PASS | `python tests/site_audit.py` — all 28 routes, 11 public-sitemap URLs, unique titles, metadata, JSON-LD and routes |
| Fictional data not indexed as job postings | PASS | Demo-focused pages are `noindex,follow`; no JobPosting structured data; no application URLs in examples |
| Original ByteBright project | NOT TOUCHED | All output is under independent `jobpath-india` local directory |
| Actual browser UI interactions | NOT VERIFIED | Chromium/Playwright navigation blocked by execution environment (`ERR_BLOCKED_BY_ADMINISTRATOR`) |
| Local HTTP integration | NOT VERIFIED | Loopback socket refused connection in execution environment |
| Live Netlify deployment / HTTPS | NOT PERFORMED | No access to a new Netlify site in this task |
| Real organization URL reachability | NOT VERIFIED | Public web browsing disabled; known reference domains still require live review |
| Current vacancies or deadlines | NOT PUBLISHED | All 10 job records explicitly fictional |
| Real mobile device / accessibility audit | NOT PERFORMED | Requires a working live browser and/or real device |
| Ads, Google Search Console verification | NOT PERFORMED | Requires website ownership, advertiser approval and actual new live URL |

## Manual QA required after deployment

- Load the homepage at the new Netlify URL and check browser developer console for errors.
- Open each route and test full navigation, search, all drop-down filters, clear filters and empty-results state.
- Save/un-save a demo and reload; check Saved Jobs persists. Turn dark mode on and reload.
- Test job details, print view, share/copy functionality and lack of false Apply buttons on examples.
- Test a real Android and iOS browser and narrow 320–390 px viewports; ensure no overlap or horizontal scrolling.
- Check all official source links for current ownership and validity, recheck privacy pages and contact method.
- Replace example host in canonical, structured data, sitemap and robots via `node scripts/configure-domain.mjs`.
- Do not submit demo listing URLs to Google Search Console or install advertising code before editorial/policy review.
