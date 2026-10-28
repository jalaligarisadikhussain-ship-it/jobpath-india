# JOBPATH INDIA — Final Web-Reviewed Release (28 October 2026)

Static independently operated government recruitment-information website. No account, no paid API, no paid hosting requirement for a small Netlify free project. This is NOT a government website.

## Source-verified public notices

- CWC 2026/01: 327 vacancies across 8 posts; last date 15 Nov 2026. Issuer: https://cwceportal.com/careers
- Railway NTPC Graduate CEN 06/2026: 3,548 vacancies; last date 6 Nov 2026. Ministry PIB https://www.pib.gov.in/PressReleaseIframePage.aspx?PRID=2321873&lang=2&reg=48
- National Insurance Company AO 321: applications close 28 Oct 2026. IBPS https://ibpsreg.ibps.in/niiclsep26/

All dates are as reviewed on 28 Oct 2026, not guaranteed indefinitely. The site calculates closure by device date and does not receive live API updates. Always check official sources for corrections.

## APPSC notice watch

15 APPSC October 2026 notice titles and numbers recorded from official https://portal-psc.ap.gov.in/HomePages/RecruitmentNotifications . These are NOT marked open or assigned unverified vacancy counts, deadlines, or eligibility.

## SSC exam notice

The official SSC Notice Board lists a 26 Oct 2026 revised-date announcement. Actual exam date rows transcribed from images supplied by the owner; the original official PDF is not yet compared, so page states provisional provenance.

## Deployment

1. Extract the production ZIP. The root must contain `index.html`, `netlify.toml`, `robots.txt`, `sitemap.xml` and `googlefcd24aba957dc07b.html`.
2. Go to Netlify → existing **jobpath-india** project → Deploys → manually deploy the extracted folder. DO NOT create a new project or select ByteBright.
3. Confirm https://jobpath-india.netlify.app/ and https://jobpath-india.netlify.app/recruitment-updates/ .
4. Check https://jobpath-india.netlify.app/googlefcd24aba957dc07b.html and sitemap.xml. No need to reverify Search Console.

## Edit jobs

In source package edit `data/jobs.json`. Verified records require source URL, official application URL, `lastVerifiedDate`, exact notice details, and appropriate verified status. For production, regenerate static HTML fallback by running `python scripts/build_final.py` and then package. Do not publish unverified posts as open.

## Known limits

No auto-refresh of government notices, no email/push alerts, no live application integrations, no deployed ads, no verified contact inbox. Search, filters, saved jobs, dark/light mode operate locally in browser. Local browser/real device final QA still recommended before any future redeploy.
