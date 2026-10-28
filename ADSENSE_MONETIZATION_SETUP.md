# JOBPATH INDIA — Advertising and revenue setup

## Current state (no ad account connected)

The repository is **AdSense-ready** but advertising is **OFF** by default. This is intentional: ad revenue is impossible until Google approves the publisher's actual AdSense account/site and ad inventory begins serving. No publisher account ID, ad-unit ID, approval or payment balance has been invented.

Live site: https://jobpath-india.netlify.app/

## Monetization workflow

1. Sign up with your own Google account at **Google AdSense**. Add the JobPath India site (current Netlify URL, if accepted for review; check account requirements). If AdSense requires a domain you own, obtain and connect one before proceeding; a domain may cost money.
2. Make sure the site has substantive, up-to-date, original and useful recruitment guidance, clear independent/non-government branding, valid contact information, working navigation, privacy terms and official source citations. Thin or duplicate pages, inaccurate vacancies and low quality content may prevent approval.
3. Complete Google's account and site ownership checks. Set up appropriate **Privacy & messaging / CMP** choices for visitors wherever required; review personalized ad and cookie consent obligations. Follow all current AdSense and local privacy requirements.
4. When you have a genuine public **publisher ID**, like `ca-pub-<16 digits>`, and actual numeric display ad **unit ID**, update `data/ads-config.json` to:
   ```json
   {
     "enabled": true,
     "provider": "adsense",
     "publisherId": "ca-pub-REPLACE_WITH_REAL_16_DIGIT_ID",
     "slots": {"content": "REPLACE_WITH_REAL_AD_SLOT_NUMBER"}
   }
   ```
   **This example is not a valid config.** Use the actual values supplied by Google, no example IDs. Never share passwords, bank details or private verification tokens with an editor.
5. On commit to `main`, GitHub checks verify the config, generated static HTML loads the approved AdSense loader, the site gets labeled responsive ad slots, and `dist/ads.txt` contains the **real** standard Google seller line. GitHub-to-Netlify deploys as usual. The `ads.txt` file is **not** generated while advertising is disabled.
6. Verify in your own AdSense dashboard that the site, ads.txt, policy/consent status and ad serving are approved. Revenue depends on legitimate viewers and eligible served ads; approval and payment are **not** guaranteed. Complete Google's payments and tax settings in your own account.

## Where ads are allowed

Only a lower-page display-ad slot on the **homepage** and certain indexable job-list categories is eligible when the real IDs are configured. An explicit **Advertisement** label prevents confusion with official recruitment instructions.

**No ads** are added inside job application actions, individual job details, auto-detected unverified notice listings, exam notices, saved jobs or the site footer. Advertising is not presented as an official vacancy or a government application button.

Advertising cannot be turned on by a script-generated ID. The strict validator stops a build with incorrect data or injection attempts.

## Privacy and user trust

The existing Privacy Policy page dynamically reflects whether Google advertising is configured. Before enabling live ads, check cookie/consent requirements, Google's Privacy & messaging settings, the published policy and visitors' regions. A simple labeled ad box **does not by itself satisfy** all legal requirements.

Do not ask visitors to click ads, click your own ads, use fake traffic, misleading "Apply" ads or payment incentives. Ad revenue is not a recruitment fee, and the site must remain clearly independent of government bodies.

## Cost and tracking

Site code, ad placeholders and GitHub-to-Netlify deployment use no paid ad APIs. Free hosting has platform limits. A custom domain is optional for the code, but may be required or helpful for AdSense eligibility and may be paid.

Check actual revenue, impressions, page RPM and policy status **inside your own AdSense dashboard**, not in a fake earnings counter on JobPath India.

**Implementation files:** `data/ads-config.json`, `scripts/validate_ads_config.py`, `assets/js/ads.mjs`, `scripts/build_final.py`, `scripts/build_dist.py`, `tests/ads.test.mjs`, `tests/test_ads_config.py`.
