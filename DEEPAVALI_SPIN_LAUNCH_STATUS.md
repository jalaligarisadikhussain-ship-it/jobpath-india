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
