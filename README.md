# JOBPATH INDIA — All-India Portal Source (Build 2.1)

**Live project to update after manual review:** https://jobpath-india.netlify.app/

**Render live (29 October 2026):** Separate static site: https://jobpath-india.onrender.com/ (39 public routes, built with `python3 scripts/build_dist.py` and published from `dist`). Netlify remains the indexed Google canonical origin; the Render copy uses cross-domain canonical tags pointing to Netlify and excludes the duplicate pages from its own sitemap. Google Analytics GA4 (`G-HFKPWNKDBY`) is opt-in on Render. Netlify production deploys are paused due to credits and its earlier site remains online. No advertising is active. See [RENDER_DEPLOYMENT_SETUP.md](RENDER_DEPLOYMENT_SETUP.md).

An independent static-first government recruitment information portal covering central, state, defence, banking, railway, teaching and SSC/UPSC resources. **Not a government website.** No paid backend, API key, website account login, or user registration is required.


## V2.1 mobile QA updates (28 October 2026)

- Replaced the SSC corrigendum's three-column horizontal scrolling table with two semantic examination cards and three date windows marked **revised proposed**, using `<time datetime>` values.
- Improved small-screen spacing in exam cards, job details, result messages, and footer for phones that show additional hosting-provider overlays. Hosting-generated floating badges are not editable in this project.
- Improved mobile navigation affordance: expanded-state icon, `aria-expanded` and Escape-to-close support. Added `prefers-reduced-motion` support and accessible, less intrusive toast messages.
- Existing Google verification file, all 38 routes, sitemap exclusions, noindex unverified content policy, and sample-only job data unchanged.
- Added regression tests for mobile exam markup and menu behavior, increasing Node tests to 25. Verified by local static/HTTP tests only; live visual browser testing is still unverified due environment restrictions.

**Deployment recommendation:** do not upload interim source versions. Use only the single `JOBPATH_INDIA_V2_1_SINGLE_UPLOAD.zip` production artifact, when ready for a deployment. The source ZIP is for editing/testing only.

## Key facts and boundaries

- **38 separately addressable pages** with responsive navigation, source directory, 28 states / 8 union territories, 8 qualification filters, exam calendar and SSC proposed exam-date corrigendum page.
- **19 recruiting-organization website references** in the source directory. They are *known reference domains, not verified live in this offline release*. Domain ownership, direct current vacancy links and latest corrections require independent verification.
- **Zero independently verified live vacancies in this package.** Only fictional examples are available via explicitly selected `/job-search/?demo=1`, labeled training data and excluded from the public default list and Google indexing. These are not job advertisements.
- **Original SSC corrigendum screenshots** supplied by the owner are summarized with the exact 26 October 2026 document wording. These are *revised proposed* examination dates, not a live recruitment notification. Direct official SSC PDF URL remains unverified, so `/exam-updates/` is `noindex,follow`.
- **Google Search Console ownership file** `googlefcd24aba957dc07b.html` is preserved at the website root. Never delete it from later deployments.
- **Adsterra prepared, advertising disabled**: JOBPATH INDIA is approved with an active native unit; its authentic code is pinned and protected by opt-in consent. Netlify production deploys are currently paused after free-credit exhaustion. See `ADSTERRA_MONETIZATION_SETUP.md`.
- **No active ads**: advertising spaces are marked for later approval, and no invented ad codes, account logins, external tracking pixels, email registration or fake apply buttons are included.
- **No automatic job alert delivery** in this static release. Theme and saved jobs are browser-local.
- **No changes** to the separate ByteBright Converter project, repository, domain or Search Console property.

## Files

- `index.html`, 37 other human-readable route folders with `index.html`, `assets/*`, `data/*`, `sitemap.xml`, `robots.txt`, `netlify.toml`, Google verification HTML: **production website**.
- `tools/job-editor.html`: **local-only editor in source ZIP**, not exposed on public hosting. It lets you import `jobs.json`, review/edit draft records, and export updated JSON. It **cannot verify data automatically**; the operator must read and verify the official notice.
- `scripts/build_final.py`: rebuild all 38 SEO pages and embed source data; update `data/jobs.json` and rebuild before redeploying.
- `scripts/package_final.py`: create production and source ZIPs.
- `scripts/validate.mjs`, `tests/*`: validation and test scripts.

## The reliability fix

Prior versions fetched all JSON files at runtime. Browser or proxy failures resulted in “Unable to load site data.” This build bundles structured editorial data into every HTML route as safe `<script type="application/json" id="jobpath-data">`. The JS uses that content first, and static HTML includes meaningful non-JS fallback content. **External JSON requests are not necessary to render the page.** After updating JSON source files, run `npm run build` so embedded content is refreshed before deployment.

## Updating a verified job safely

1. On the *actual recruiting body's website*, confirm advertisement and reference number, recruitment title, source domain, original official notice PDF, applying URL, qualifications, pay/vacancies only if stated, start/last date, and any corrigenda. Keep the last verified date. Do not infer missing data.
2. Open `tools/job-editor.html` locally from the source package; import `data/jobs.json` and edit. If the notice is unverified, leave `verified=false` and `status="unverified"` so it is **not** publicly displayed. Verified records require actual HTTPS notification/application URLs and verification date.
3. Download JSON from the editor and replace **only** the source `data/jobs.json` in this project. Keep a backup of prior records.
4. Run checks:

```bash
npm run build
npm test
npm run validate
python3 tests/site_audit.py
python3 scripts/package_final.py
```

5. Upload **only the production ZIP/extracted production folder** to the existing Netlify `jobpath-india` project. Verify the real pages and live official links again after publication.

**Never upload the entire SOURCE ZIP to Netlify** because it contains an offline editor, tests and development scripts. **Do not create a new Netlify project or modify ByteBright.**

## Search Console and SEO

- Site URL: `https://jobpath-india.netlify.app/`
- Sitemap: `https://jobpath-india.netlify.app/sitemap.xml` (19 indexable guide, directory and informational pages in this release).
- Ownership file preserved: `https://jobpath-india.netlify.app/googlefcd24aba957dc07b.html`.
- Keep the existing URL-prefix property. **No need to re-verify or resubmit the unchanged sitemap URL after a content update.** Google will crawl based on its own schedule; there is no indexing or traffic guarantee.
- Routes containing fictional records or an independently unverified SSC document remain `noindex,follow`. Never add JobPosting structured data until a *real, valid, individually verified* job opportunity exists.

## Coverage and accurate publishing

| Area | Included | Not claimed |
|---|---|---|
| Government jobs | Search, filtering, status/deadline logic, job details and bookmarks | Real current openings without independent verification |
| Geography | 28 states + 8 union territories | Vacancies in every state or an active department portal for each |
| Sources | 19 organization reference links and guidance | Live verification of all links, endorsement or government affiliation |
| Exam updates | SSC 2026 screenshot transcription and exam-calendar guide | Official final schedule or a new recruitment vacancy |
| Admin | JSON import/export offline editor and CLI validator | Remote admin login, server database or one-click online publish |
| Alerts | Browser-local saved jobs | Email, SMS, notifications or automated monitoring |
| Advertising | Placeholder areas, privacy / editorial policy | Live ads, ad-network approval, revenue |

## Manual release QA checklist

- Verify homepage, latest jobs empty state, 38 page routes, source-card search/category filter, 28+8 region links, qualifications and demo-mode filters.
- Verify saved job persistence, dark/light switch, mobile menu, keyboard focus, print and copy actions in a real browser.
- Verify the Google HTML file, `/robots.txt` and `/sitemap.xml` on the final Netlify URL.
- Open official organization sites to check current ownership, source link changes and any notice amendments. The build process cannot do this without live source browsing.
- Confirm new and updated content is responsibly indexable and does not imply that fictional test data is live.

## 30-day editorial cycle

Days 1–5: recheck official-domain references; days 6–10: review original recruitment notices; days 11–15: verify examination calendar updates; days 16–20: improve state-wise resources; days 21–25: fix accessibility/expired records; days 26–30: evaluate crawl status, content quality and corrections. Repeat only with real sourced material.

### Automated testing limits

This build includes 25 automated Node tests, including actual execution of all 38 page renderers with external JSON fetch deliberately denied, plus static metadata/asset/route audits. Chromium browser navigation was denied by the execution environment (`ERR_BLOCKED_BY_ADMINISTRATOR`), so true visual desktop/mobile browser QA and real-device compatibility have **not** been verified. Deployment itself is not performed in this deliverable.

For release quality evidence, read `RELEASE_QA.md`.


## Optional Google Analytics 4 integration (29 October 2026)

- Web stream: JOBPATH INDIA Website; Measurement ID: G-HFKPWNKDBY.
- assets/js/analytics.mjs uses visitor opt-in: no Google tag request is made until Allow analytics is selected. Visitors can decline or change their choice through Analytics choices in the footer.
- Analytics helps measure page views and engagement for consenting visitors only. Tracking blockers or a declined preference prevent collection.
- The generated 38-page site includes the analytics module through scripts/build_final.py, and scripts/build_dist.py includes the asset in the published directory.
- Privacy notices were updated; advertising remains disabled and separate from analytics consent.
- To activate on the live site, deploy the latest main build to the existing hosting project. If Netlify deploys are paused because credits are exhausted, the repository change alone does not activate live collection.
- Test by visiting the published site, allowing analytics, and checking Google Analytics Reports > Realtime. Realtime reporting can be delayed.
