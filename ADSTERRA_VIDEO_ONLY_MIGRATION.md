# JobPath India — Adsterra video-only migration request
Updated 2026-10-31

**Status: awaiting Adsterra publisher support confirmation and site-specific video ad tags. This document is a request/implementation checklist, NOT proof of account-side filtering or video ad activation.**

## Site and existing units
- Primary Cloudflare site: https://jobpath-india.pages.dev/
- Existing configured site identifier: 6159057 (publisher should verify host association with Adsterra)
- Active code families: Adsterra Native Banner and 320×50 / 728×90 / 300×250 display banner scripts.
- The existing units are **not** a verified video format.
- Current live ad behavior is intentionally preserved until a supported replacement has been received and tested.

## Requested publisher-side settings
1. Prefer **video creative inventory only**, if an Adsterra-supported outstream format is available for informational job websites without an original video player. Otherwise confirm VAST/in-stream requirements rather than inserting an ad-only video player.
2. Prefer legitimate educational services, exam preparation, professional courses, technology, productivity, reputable employment services and mainstream consumer brands. These are *preferences*, not guarantees.
3. Request exclusion of gambling, betting, casino, adult, dating, misleading hiring, malware/downloads, deceptive financial/crypto get-rich-quick promotions, aggressive popunders and automatic redirects. Obtain written confirmation of which filters are supported per site and format.
4. The actual advertising creative and category restrictions can only be guaranteed to the extent of Adsterra's server-side controls and review mechanisms. Frontend JS cannot reliably classify or reject video content inside cross-origin ad frames.
5. Preserve advertising labeling, existing visitor privacy choices and compliance obligations. No forced pre-application video gate, auto-opening tabs or video autoplay with sound.

## Before switching the live site to video only
- [ ] Adsterra confirms the publisher site and that video-only inventory is actually supported for this content type.
- [ ] Obtain the exact site-specific approved video/VAST/outstream tag, placement ID, consent rules and code integration documentation. **Never manufacture an ad tag.**
- [ ] Confirm creative exclusions on the relevant publisher account/site and test their enforcement.
- [ ] Confirm original video content requirements; do not use fake or unrelated content as an excuse to trigger in-stream ads.
- [ ] Build an optional video placement with accessible controls, clear ad labeling and a no-fill fallback; never block job links or require watching an ad to apply.
- [ ] Test Chrome/Instagram WebView, mobile/Desktop, muted playback, no-fill, opt-out, GPC, relevant geography and navigation.
- [ ] After successful tests, disable native/banner Adsterra **in the same release** that activates the replacement. Avoid intentionally leaving monetization broken before an approved replacement exists.
- [ ] Document the actual Adsterra server-side filter confirmations and update the live privacy disclosure.
- [ ] Confirm Cloudflare live deploy and inspect the actual creative in a browser; code and successful CI alone do not verify ad display.

The AdSense account verification/approval and all other sites are independent of this migration.
