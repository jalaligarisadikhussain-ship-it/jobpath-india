# Deepavali Dhamaka 2026 — launch status

**Status: demo preview, NOT an active giveaway.**
Public preview: https://deepavali-dhamaka-spin-2026.onrender.com/
Source branch: `deepavali-spin-2026` (isolated from JobPath India production branch).

## Completed in demo
- Mobile-friendly 6-sector festive wheel.
- Clearly disclosed Stage 1: the warm-up spin always ends on Try Again (no prize or draw entry). It is not presented as a fair chance to win.
- Stage 2 after the warm-up: one free demo gift-draw spin (no real rewarded ad connected), selecting one of five sample entries at random, 20% each: Flipkart 50%-offer draw entry; Amazon 50%-offer draw entry; Meesho 50%-offer draw entry; ₹500 draw entry; ₹1,000 draw entry. These are *not* real offers, coupons or prizes and the merchants are not sponsors.
- Result modal presents two clearly labeled sharing tasks: 20 distinct WhatsApp participants and 5 group shares.
- WhatsApp deep-link sharing, copyable invitation URL and 5-group invitation button. Removed the misleading 'I shared' completion button, progress bar and browser-only self-reports; any previously saved group-claim count is discarded. The five-group status remains 0/5 verified until independent verification is available. Cannot verify actual WhatsApp group posts or unique human referrals from this static frontend.
- Public reset control remains removed. An unlisted browser-local replay shortcut exists at `?demo_replay=1` for testing; opening it deletes only that browser's *demo spin state* and restarts the warm-up. It is not authenticated and is NOT a genuine owner-only security feature. Replays turn on per-tab test mode and suppress all optional ad calls to avoid invalid repeat impressions. An explicit Exit demo test mode button clears this tab-only test flag; neither actual prizes nor real referral records are affected.
- Results placeholder for November 8, 2026, at 8:00 PM IST, with no invented winners.
- Privacy/terms disclosures; preview is noindex to prevent search users mistaking sample offers for real ones.
- **Current advertising (4 November 2026):** ONLY Adsterra Social Bar **32077118** (approved site-specific script `bauval.org/14/f17978bd575f15f7a0cec124a9d91646`) is enabled. Its script is near the closing body tag and respects the saved visitor ad opt-out, Global Privacy Control, and demo replay. Popunder **32076389** was removed from the live site's HTML/script loading at the organizer's request after an unrelated external prize-wheel page appeared. Native Banner **32071962** remains in the source but its load flag is OFF. The website displays script-load status but does not claim creatives have rendered. Advertiser inventory, content, and category exclusions remain under network control; the previously seen misleading floating Facebook-recovery ad remains a possible brand-safety concern. Free demo spin requires no ad engagement. Review consent and ad category safety before increasing public traffic.

## 1–5 tracking development (4 November 2026)

- **1. Tracking backend:** Built a separate Node/Express API on Render free web service `deepavali-dhamaka-tracking-api` (URL: https://deepavali-dhamaka-tracking-api.onrender.com). This runs alongside the existing static site; the demo prize logic remains unchanged.
- **2. Referrals:** Server-side Postgres schema, consented participant enrollment, signed-in participant status and public aggregate-only count endpoints. A new registration is `pending` until the organizer independently checks it; only `verified` registrations are counted as referrals.
- **3. WhatsApp groups:** Up to five voluntarily submitted, redacted screenshots with unique group labels per member; status `pending / approved / rejected`. These are **human review statuses**, not WhatsApp API delivery confirmation.
- **4. Admin:** Password-protected Render API dashboard with signed Secure/HttpOnly session, private screenshot preview, status approvals/rejections, and image removal. Security values live in Render environment variables, never in the repository.
- **5. Monetization:** Existing Adsterra **Social Bar only** remains enabled on the public spin site, while Popunder and Native Banner remain disabled.
- **Privacy isolation:** Participant bearer tokens, emails and submitted images stay on an **ad-free tracking origin**. The public ad-supported wheel stores only an intentionally shareable referral code and can fetch aggregate counts without a private token.
- **Current launch blocker:** Render free Postgres `deepavali-dhamaka-tracking-db` has been created, but the Render API service's **DATABASE_URL must be privately linked** to its Internal Database URL in the Render dashboard. Until this is completed and `/healthz` returns database connected, enrollment remains disabled and **live tracking must not be advertised as operational**.
- **Database expiration:** free Postgres is scheduled to expire **4 December 2026**. Plan a persistent storage move/upgrade with explicit budget approval before accepting real campaign registrations.
- **Real gifts (6):** intentionally unchanged and disabled. There is no real sponsored Flipkart, Amazon, Meesho coupon or funded cash prize.

## Organizer-only tracking visibility (4 November 2026)

- Public spin page no longer shows `0/20`, `0/5`, referral progress bars, group-review statuses, or a public tracking dashboard. Visitors can still spin, share invitations, register voluntarily, and submit redacted screenshots.
- Public registration page omits verification totals and group-review outcomes; the administrator sign-in link was removed from its footer.
- Public `/api/public-counts/:code` endpoint was removed, and `/api/me` no longer returns referral/group totals.
- **Only** the password-protected organizer dashboard at `https://deepavali-dhamaka-tracking-api.onrender.com/admin` has the approval and tracking controls; the URL alone does not grant access.
- Tracking backend database connection `DATABASE_URL` remains required. Do not claim enrollment/verification operational until /healthz reports a connected database.
- Adsterra Social Bar remains enabled; Popunder and Native Banner disabled. Demo prizes unchanged.

## Registration-free public flow (4 November 2026)

- Viewers open the main Spin & Win URL and can start the two-stage demo directly; **no registration or email entry is needed**.
- On mobile, the page scrolls to the wheel when opened via the normal URL. The public invitation URL points to `/#spinGame`, which opens directly at the wheel on any screen.
- After the sample gift spin, **Task 1** offers WhatsApp sharing with 20 interested people and **Task 2** with 5 groups that allow invitations. Both WhatsApp buttons work without a signup.
- After watching the user's screen recording (4 November 2026), fixed a false completion issue: the Web Share API can resolve at a device handoff before WhatsApp's actual Send operation. The 0/20 and 0/5 automatic counters, share-open counting and self-reported/manual counters have therefore been removed from the viewer page. Public buttons open the WhatsApp deep link directly without increasing any completion metric; the page still shows 20 PEOPLE and 5 GROUPS goals. This static site cannot detect which contacts/groups received a message, and no prize eligibility is inferred. Previously stored click/handoff counts are no longer read.
- Public registration links and public proof-submission links have been removed from the spin page. Legacy `/participate.html` and API `/join` pages redirect to the wheel, not to a signup form.
- The standalone API's password-protected organizer dashboard is preserved and hidden from public navigation. Without participant registrations or independent proof, **20/20 and 5/5 cannot be automatically verified**. No fake completion counters or identity claims are shown.
- Adsterra Social Bar stays ON; Popunder and Native Banner stay OFF. Gift outcomes remain **demo-only**, with no funded or redeemable prizes.

## Anonymous referral tracking and 5-group screenshots (4 November 2026)

- Added `dd_anon_players` and `dd_anon_proofs` Postgres schema and API endpoints `/api/anon/start`, `/api/anon/play`, `/api/anon/me`, `/api/anon/proof`, and `/api/anon/me` DELETE; no registration, email, phone or OTP.
- Anonymous per-browser referral code is added to shared wheel URL. A referral counts only after the receiving browser starts a spin, once per browser token. Counters are 0/20 unique browser plays, not 20 verified people and not WhatsApp sent events; deleting storage may generate duplicates.
- Optional group-proof screenshots use separate ad-free API-origin `/proof` page. At most five distinct group labels, JPEG/PNG/WebP images compressed below 900 KB, prior redaction/consent; statuses pending/approved/rejected controlled only in password-protected `/admin`.
- Admin dashboard now includes anonymous browser totals and group-proof queue. No public access to submitted images.
- **Launch blocker**: `DATABASE_URL` must still be set privately on the Render tracking API service to connect the free Postgres (expires December 4, 2026). Until connected, the public site says tracking unavailable and continues to allow the free demo spin without inventing counters.
- Social Bar unchanged/on, Native Banner and Popunder remain off. Demo prizes remain inactive.

## Viewer screenshot step removed (November 4, 2026)

- Removed the screenshot submission button and public 0/5 pending/approved screenshot counter from the Spin & Win viewer interface. 20-browser referral tracking remains available.
- The 5-group sharing goal is still visible, but it does **not** imply automatic WhatsApp send/delivery verification.
- Existing uploaded proof records and private administrator review/deletion tools remain intact. No private images were automatically deleted.
- The legacy ad-free proof endpoint remains for existing participants' records; it is no longer linked from the public wheel.

## Popunder re-enabled at organizer request (November 4, 2026)

- Adsterra site-specific **Popunder_1 placement 32076389** (`https://abscloud.org/1/3110baa332934e98a495157335d1404f`) is back in the static site, once per page, alongside Social Bar **32077118**.
- Popunder and Social Bar both respect visitor opt-out stored in `deepavali_native_ad_consent_v1`, Global Privacy Control, and owner demo replay. Native Banner remains OFF. No ad engagement is required to spin.
- Script load success is **not** proof that an advertisement is shown; browser popup blockers, network policy, frequency limits and inventory apply. Earlier misleading pop creatives can recur until the Adsterra publisher account blocks unsafe advertiser categories. Review category filters promptly.

## Must be completed before a public prize promotion
1. **Prizes and authority:** Organizer must obtain genuine redeemable inventory and written permission for brand-specific discount claims (and discount limitations) or remove those brand references; publish organizer identity, eligibility rules, number of winners, drawing method, claim deadlines and contact details. Never imply an unaffiliated merchant sponsors the campaign.
2. **Rewarded video approval:** Obtain written consent from the ad network for *incentivized/rewarded viewing*. Use its sanctioned SDK, complete-view postback and anti-abuse verification. Do not substitute a regular banner, iframe or simulated five-second watch. The current retry is free.
3. **Referrals:** Deploy a server-side database and enrollment flow. Count only legitimate distinct joiners using a privacy-preserving anti-abuse method; link clicks/forwarding alone do not qualify. State how participant data are collected, retained and deleted.
4. **WhatsApp group activity:** WhatsApp does not grant arbitrary websites proof of sharing to five distinct groups. The self-report checkmarks have been removed. Do not treat WhatsApp share-screen opens as proof, call group posts objectively verified, or make an unprovable group-sharing condition part of an actual prize. Either remove this as an eligibility condition or design an opt-in, auditable alternate condition.
5. **Admin:** Admin authentication with proper session security and audit logs is required before any administrative reset, approval, fraud review or results publication. Never hide an insecure admin PIN in a static page.
6. **Drawing:** Freeze qualified entries after closing, run documented random selection server-side, record an audit trail and only publish genuinely selected winner results; contact winners privately.
7. **Compliance / privacy:** Review local promotional-prize rules, platform advertising rules, consent/privacy notices, and required terms before activation.
8. **Testing:** Test on Android/iOS browsers, repeat refresh, concurrent users, self-referrals, duplicate signups, ad failures, share cancels, countdown time zone, accessibility and low network speed.
9. **Indexing:** Remove the preview noindex tag only after a real campaign with compliant terms has been activated.

## Safe demo state
Users can test the wheel and see the sample share instructions. They cannot win an actual prize, trigger verified rewarded ads, or satisfy real referral criteria on this preview. Keep this message clear to visitors.
