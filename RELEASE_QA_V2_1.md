# JobPath India — V2.1 Quality Assurance

Date: 28 October 2026. Isolated development copy; existing Netlify and ByteBright sites unchanged by this build.

## Implemented

- Replaced sideways scrolling SSC exam dates table with accessible stacked responsive cards, keeping both JE date windows and the SI date window distinct.
- Preserved exact original screenshot-derived dates and their **proposed** status, the verification-pending notice, and noindex for unverified exam updates.
- Improved mobile spacing, search empty-state padding, responsive job metadata, and footer clearance for page-bottom overlay interference. The platform-generated Netlify branding/badge is outside this site's source code and cannot be guaranteed to disappear via CSS.
- Improved menu expansion label/icon and support for closing on Escape; added reduced-motion preference and a mobile-friendly toast location.
- Retained all 38 routes, 19 indexable sitemap URLs, original Google ownership verification file, no fake public vacancies, zero active ads, and no ByteBright dependencies.

## Local verification

- 25/25 Node automated tests — pass.
- JSON jobs and source integrity validation — pass.
- HTML metadata/SEO, all internal local links and sitemap audit — pass.
- Local HTTP 200 checks, 38 routes and root assets — run as part of final release QA.
- ZIP CRC, file membership, clean production/source separation — run as part of final release QA.

## Not verified

- Live Chrome/mobile visual behavior: available headless Chromium process timed out in this environment; no visual screenshot could be generated. The user should check this version on a real phone after deployment.
- Current government vacancies/URLs/official direct notification PDFs: live internet research disabled; do not display an unverified vacancy as active. User-supplied SSC images are not independent official PDF verification.
- Live Netlify deployment: this package is not pushed automatically; all deployment instructions target the existing `jobpath-india` project only.
- Google indexing and advertising eligibility/revenue: outside source-code testing; no guarantees.
