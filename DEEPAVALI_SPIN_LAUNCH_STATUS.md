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
- **Current ad format test (3 November 2026):** Adsterra Social Bar for this exact Render domain, placement **32077118**, is the **only enabled ad script**. The script is appended once immediately before the closing body tag; it is protected by the visitor's saved ad preference, Global Privacy Control, and demo replay test mode. The previous Native Banner placement **32071962** remains in the source but its loading flag is OFF. The approved Popunder placement **32076389** has been removed from the active page. The Social Bar's floating position and whether creatives render are controlled by Adsterra; a successful script-load event does **not** prove an ad was displayed. Mobile testing showed script-loaded status without a visible creative. This site cannot force Social Bar to appear as a top fixed banner using the present ad tag. A separate, site-specific, approved display banner tag would be required for a predictable top placement. An ad opt-out is available in the footer. Confirm network-side placement, inventory, geographical targeting and category restrictions with Adsterra before scaling. Ad clicking or ad viewing is never required for the free demo spins; no rewarded-video SDK exists.

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
