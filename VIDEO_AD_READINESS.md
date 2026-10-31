# JOBPATH INDIA — Professional outstream video readiness

Status: **code prepared in a separate branch, NOT a live video ad**. Existing Cloudflare Adsterra native and banner placements are not modified.

## What has been prepared

- `data/video-ads-config.json` starts disabled with no fake video URL or provider code.
- `assets/js/video-ads.mjs` can mount **one** explicitly labeled, independently closable in-page 16:9 video iframe after a content section, only on the exact `jobpath-india.pages.dev` hostname.
- `assets/js/app.mjs` reads the config after the existing page has rendered. If pending/invalid, it adds no ad or blank placeholder and triggers no video request.
- Real video loading requires an explicitly saved `allow` advertising choice (not publisher-default banner display); saved denial and Global Privacy Control suppress it.
- Do not claim an iframe enforces muted playback: verify the approved provider video actually defaults to muted and is closable on mobile and desktop.

## Prerequisites to activate

1. Apply honestly to an established video monetization provider, starting by evaluating VDO.AI; disclose true traffic, job website content, ownership and Cloudflare Pages URL.
2. Confirm **outstream** eligibility for `https://jobpath-india.pages.dev/`. Approval and payout terms are presently unknown.
3. Ask the provider for written controls or exclusions for gambling/casino, adult/dating, fake job offers, misleading download buttons and forced redirects. A local boolean flag does not enforce creative filtering on provider servers.
4. Obtain the **real approved iframe embed URL** and exact provider hostname. If provider supplies VAST/script instead, **do not** put it in `embedUrl`; implement the vendor-supported adapter first.
5. Verify muted autoplay, accessible pause/close behavior, mobile functionality, privacy/CMP obligations and clear labeling on actual test inventory.
6. Only then set `enabled:true`, `status:'approved'`, `provider:'vdo.ai'` (or the actual approved provider), `publisherApproved:true`, `categoryExclusionsConfirmed:true`, `mutedPlaybackVerified:true`, `closeControlVerified:true`, `embedUrl` and `embedHost`.
7. Test `node --test tests/video-ads.test.mjs`, existing ads/tests, deploy on the correct Cloudflare branch and verify without clicking paid creatives or generating artificial impressions.

**Do not merge solely to activate paid video:** the feature intentionally fails closed until actual network approval, codes and manual QA. Additional video inventory raises ad density; audit against provider policies and visitor experience.

Unchanged: `data/ads-config.json`, `assets/js/ads.mjs`, existing ad scripts, job data, publishing automation, Netlify, Render, ByteBright, RoleGlobe and game sites.
