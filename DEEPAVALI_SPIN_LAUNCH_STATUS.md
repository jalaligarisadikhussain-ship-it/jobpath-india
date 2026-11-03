# Deepavali Dhamaka 2026 — launch status

**Status: demo preview, NOT an active giveaway.**
Public preview: https://deepavali-dhamaka-spin-2026.onrender.com/
Source branch: `deepavali-spin-2026` (isolated from JobPath India production branch).

## Completed in demo
- Mobile-friendly 6-sector festive wheel.
- Random first spin across all six equal sectors; the same unbiased randomness applies to the optional second spin, which is available only after a first-spin Try Again.
- One free demo retry only after a first-spin Try Again; six random outcomes (Try Again plus five sample entries), each 1 in 6, so a retry does not guarantee a gift-draw entry. Five sample entries: Flipkart 50%-offer draw entry; Amazon 50%-offer draw entry; Meesho 50%-offer draw entry; ₹500 draw entry; ₹1,000 draw entry. These are *not* real offers, coupons or prizes and the merchants are not sponsors.
- Result modal presents two clearly labeled sharing tasks: 20 distinct WhatsApp participants and 5 group shares.
- WhatsApp deep-link sharing, copyable invitation URL; 5-group button and browser-only self-report progress. Cannot verify WhatsApp group shares; cannot count actual unique human referrals from this static frontend.
- Public reset control removed; the existing browser's demo spin state stays in localStorage. Not tamper-proof, does not confer real eligibility.
- Results placeholder for November 8, 2026, at 8:00 PM IST, with no invented winners.
- Privacy/terms disclosures; preview is noindex to prevent search users mistaking sample offers for real ones.
- No real third-party ad script is installed; no claim that watching an ad earned an attempt.

## Must be completed before a public prize promotion
1. **Prizes and authority:** Organizer must obtain genuine redeemable inventory and written permission for brand-specific discount claims (and discount limitations) or remove those brand references; publish organizer identity, eligibility rules, number of winners, drawing method, claim deadlines and contact details. Never imply an unaffiliated merchant sponsors the campaign.
2. **Rewarded video approval:** Obtain written consent from the ad network for *incentivized/rewarded viewing*. Use its sanctioned SDK, complete-view postback and anti-abuse verification. Do not substitute a regular banner, iframe or simulated five-second watch. The current retry is free.
3. **Referrals:** Deploy a server-side database and enrollment flow. Count only legitimate distinct joiners using a privacy-preserving anti-abuse method; link clicks/forwarding alone do not qualify. State how participant data are collected, retained and deleted.
4. **WhatsApp group activity:** WhatsApp does not grant arbitrary websites proof of sharing to five distinct groups. Current checkmarks are **self-reported**. Do not call this objectively verified or make unprovable group-sharing a condition for an actual prize. Either remove this as an eligibility condition or design an opt-in, auditable alternate condition.
5. **Admin:** Admin authentication with proper session security and audit logs is required before any administrative reset, approval, fraud review or results publication. Never hide an insecure admin PIN in a static page.
6. **Drawing:** Freeze qualified entries after closing, run documented random selection server-side, record an audit trail and only publish genuinely selected winner results; contact winners privately.
7. **Compliance / privacy:** Review local promotional-prize rules, platform advertising rules, consent/privacy notices, and required terms before activation.
8. **Testing:** Test on Android/iOS browsers, repeat refresh, concurrent users, self-referrals, duplicate signups, ad failures, share cancels, countdown time zone, accessibility and low network speed.
9. **Indexing:** Remove the preview noindex tag only after a real campaign with compliant terms has been activated.

## Safe demo state
Users can test the wheel and see the sample share instructions. They cannot win an actual prize, trigger verified rewarded ads, or satisfy real referral criteria on this preview. Keep this message clear to visitors.
