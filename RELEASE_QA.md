# JOBPATH INDIA — Final Local Release QA

**Build:** 2.0 · **Date:** 28 October 2026 · **Destination:** existing `jobpath-india` Netlify project

## Verified locally

| Check | Result | Evidence |
|---|---|---|
| 38 route builds, 19 indexable page URLs | PASS | `npm run build`; generated page metadata and sitemap |
| Local site data embedded in every page | PASS | `tests/final_features.test.mjs` |
| Runtime page rendering with external JSON fetch blocked | PASS | `tests/runtime_pages.test.mjs`: all 38 page routes rendered |
| 23 automated tests | PASS | `npm test`: 23/23 |
| Source, date, URL, unique identifier and file validation | PASS | `npm run validate` |
| Static SEO, internal routes, linked assets, canonical and sitemap | PASS | `python3 tests/site_audit.py` |
| Local HTTP route and asset checks | PASS | 38 pages + 7 critical files returned HTTP 200 from local Python server |
| 28 states + 8 UTs; 19 organization references | PASS | Data integrity tests |
| Google site ownership file preserved | PASS | `googlefcd24aba957dc07b.html` in root and production ZIP |
| Real vacancy misrepresentation avoided | PASS | All sample jobs are `isDemo: true`, `verified: false`, hidden from public-default listings; SSC screenshots labeled verification pending |
| Production ZIP integrity and public-source separation | PASS | Zip CRC validation; production ZIP excludes local editor/tests/scripts |
| ByteBright Converter modified | NO | Development isolated to new `jobpath-india-final` workspace |

## Cannot verify here

- Real external government websites, live vacancy notices, notice PDFs and official apply URLs were **not verified** because live public browsing is disabled. The reference links are known research starting points and may have moved or changed.
- Chromium/Playwright browser navigation was blocked by environment policy (`ERR_BLOCKED_BY_ADMINISTRATOR`) for both localhost and local file pages. This means **visual UI, accessibility, real mobile browser, keyboard and interaction-based end-to-end tests are not independently verified**. Unit tests cover filter/search functionality; DOM render mocks cover page templates.
- Live Netlify deployment has **not been performed for this new version**. The user's existing deployed V1.x website remains unchanged until they manually replace it with the new release.
- Google indexing is controlled by Google; existing Search Console verification and prior sitemap success do not prove current pages are indexed.
- Ads, opt-in email notifications, push alerts and actual real jobs are not activated in this release.

## User's single-upload checklist

1. Back up any locally added job records or notice edits from the existing project.
2. Extract `JOBPATH_INDIA_FINAL_ONE_UPLOAD.zip` in Windows. Check that `index.html`, `sitemap.xml`, `googlefcd24aba957dc07b.html` appear directly in the extracted folder.
3. Netlify → **Projects → jobpath-india → Deploys** → manual deploy; drag and drop the entire extracted folder. **Do not create another project. Do not select ByteBright.**
4. Check status **Published**, then visit https://jobpath-india.netlify.app/; refresh with `Ctrl + Shift + R`.
5. Check `/states-directory/`, `/official-sources/`, `/application-guide/`, `/exam-calendar/`, `/job-search/`, `/exam-updates/`, `/sitemap.xml` and the Google verification file.
6. Keep the same Search Console URL-prefix property and sitemap URL; no repeated ownership verification is normally required.
7. Open at least one current organization source manually, inspect mobile navigation and sample training mode. Do not publish actual vacancy details until verified.

**Note:** Netlify free-tier limits remain subject to the service's usage policy. There is no paid API dependency in the site, but hosting limits and future domain/advertiser fees cannot be guaranteed at ₹0 in every circumstance.
