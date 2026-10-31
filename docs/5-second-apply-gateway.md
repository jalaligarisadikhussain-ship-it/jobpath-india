# JobPath India | 5-second Apply gateway

## Current state
Review branch only. The production main branch is unchanged.
Feature switch: JOB_GATEWAY_ENABLED = false in assets/js/app.mjs.

## Frontend
- assets/js/job-gateway.mjs: secure destination check, monotonically timed 5000ms countdown, disabled Continue button, accessible dialog, cancel/Escape, focus trap, no popup blocker dependency, mobile support.
- assets/css/job-gateway.css: premium responsive styles and labeled reserved sponsored slot.
- tests/job-gateway.test.mjs: timer boundaries, URLs, modified clicks, inactive behavior.
- assets/js/app.mjs: binds only source-verified, non-demo, non-closed job application URLs; verifies destination matches record before interception.

## Ad-network policy gate
NO third-party ad script was added. The gateway slot is intentionally an empty, labeled placeholder.
This is NOT an AdSense Vignette implementation; that placement is controlled by Google.
Adsterra Social Bar and Direct/Smart Links must not be embedded into this slot or substitute for the official job destination.
Before enabling it, obtain written approval from the chosen network for a forced five-second countdown in front of external job application navigation, get a dedicated display/native ad unit approved specifically for the gateway, and comply with regional consent requirements.
Respect saved opt-outs and browser Global Privacy Control.
Even with approval, never require visitors to click an advert; the only Continue action points to the source-verified HTTPS application URL.

## Launch sequence
1. Confirm ad format and category restrictions with the provider; no premium CPM is guaranteed.
2. Add only the approved gateway creative inside the mountApprovedAd(slot) callback (do not reuse current homepage tags).
3. Review ad disclosures, user consent, performance and accessibility, then change JOB_GATEWAY_ENABLED to true in app.mjs.
4. Run npm test; npm run validate; python3 scripts/build_dist.py; python3 tests/site_audit.py.
5. Open a review PR, check all CI jobs and deploy to Cloudflare Pages only after approval.
6. Track valid served impressions, fill rate, revenue, viewability, job-link abandonment, Core Web Vitals and conversions; revert the feature if access or trust degrades.

## Important
A blank timed gate is not a sensible live monetization experience. Keep the switch off if there is no approved creative.
