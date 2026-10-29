# JOBPATH INDIA — Adsterra monetization setup

## Current status — 29 October 2026

The existing Adsterra publisher account was reused. JOBPATH INDIA was registered as a separate website and the authenticated dashboard confirmed:

| Item | Verified value |
| --- | --- |
| Website | `jobpath-india.netlify.app` |
| Website ID | `6159057` |
| Website status | **Approved** |
| Native banner unit | `NativeBanner_1` |
| Ad unit ID | `31978670` |
| Ad unit status | **Active** |
| Widget layout | `2:1` (saved in Adsterra) |
| Adult advertising | **Off** (confirmed in About Website) |
| Gambling category exclusion | **Not confirmed**; adult-off is not a gambling filter |
| Website-side advertising | **Disabled** in `data/ads-config.json` |

Approval is an observed account status, not a promise of future eligibility, impressions, revenue or payment. No publisher information from another website was reused. JOBPATH INDIA, ByteBright and other projects remain separate.

## Genuine public ad tag

The account supplied this exact tag for JOBPATH INDIA:

```html
<script async="async" data-cfasync="false" src="https://bauval.org/21/59088646af2816821f7d8b37df198113"></script>
<div id="container-59088646af2816821f7d8b37df198113"></div>
```

This is public installation code, not a password or API secret. The Python validator and browser module pin this website, unit, script URL and container. The runtime also refuses native ad requests outside the approved `jobpath-india.netlify.app` hostname, including localhost and unrelated projects. A new key, host or path requires a reviewed code change. Do not add tracking parameters or use another publisher's code.

`assets/js/ads.mjs` reproduces the supplied script attributes and adjacent container only after opt-in. The tag is not placed in an iframe. Only native unit `31978670` is included in this implementation. The dashboard also shows Popunder and Social Bar units for this site; their tags were not copied, installed or executed by this integration. No Smartlink or fake application link was added. Placements remain below content on the homepage and the existing eligible job-category pages; job details, application actions and unverified automatic notices have no ad placements.

## Privacy and consent implementation

The prepared privacy page identifies Adsterra, links its privacy/cookies policies, explains relevant browser/device data and advertising interactions, and describes user choices. If ads are later enabled:

- Advertising starts off until the visitor chooses **Allow advertising**.
- **Continue without ads** keeps recruitment information fully available.
- The versioned allow/decline preference is saved locally for up to 180 days.
- **Advertising choices** in the footer and privacy page lets a visitor change or withdraw consent. Withdrawal refreshes the page to stop an already-running ad script.
- Global Privacy Control keeps native advertising off. Unavailable storage fails closed.
- There is no preconnect, ad script, iframe or ad request before consent.

These measures implement the documented site behavior; they do not constitute a legal certification or a guarantee about third-party campaign content. Adsterra's publisher terms require privacy disclosure and a cookie-consent message when cookies are used. Continue to review policies and applicable visitor-region requirements before activation.

Adult ads are disabled. Gambling-category exclusion has not been confirmed in the self-service controls. The owner can authorize a support request to exclude gambling/betting campaigns for this site and unit before activation. No support message has been sent.

## Deployment blocker — confirmed in Netlify

The existing Netlify project is connected to this GitHub repository and auto-publishing from `main` is on. The account reports that production deploys are paused because its available deployment credits are exhausted. Recent GitHub commits were **Skipped due to account credit usage exceeded**. Operational credits keep the published site online but cannot fund production deploys.

The displayed billing period is **28 October–27 November 2026**. Netlify says to wait for the next billing cycle or upgrade. No upgrade, payment method, credit purchase or paid service was activated. Do not promise an exact resumption time until Netlify confirms it. No hosting migration was performed.

The last published commit observed in Netlify was `aee15aaaeea09216212f66fa82d77ba8683efbff`, so the currently public site serves an earlier release. The live `/data/ads-config.json` and `/auto-recruitment-notices/` paths returned HTTP 404 during the prior deployment check. The GitHub automation remains in place, but newly generated website changes cannot become public while production deployment is paused.

The repository's intended build command is `python3 scripts/build_dist.py` and publish directory is `dist`. Publishing this prepared integration requires deployment capacity on the existing host, or explicit authorization for a separate free hosting option and any resulting URL/ad-network changes.

## ads.txt

No Adsterra seller line was supplied by the website registration or Get Code interface inspected in this setup. No seller record was invented. The current site has no ads.txt. The build emits Google's standard seller line only for an enabled AdSense provider, never for Adsterra. Confirm any applicable Adsterra ads.txt instructions in the account or with support before activation; add only actual provider-supplied records.

## Checks completed

- Netlify production build: **39 routes**, **25 sitemap URLs**.
- JavaScript tests: **41 passed**, including opt-in, refusal, expiry, withdrawal, Global Privacy Control, duplicate-load protection, storage errors, approved-domain restrictions and exact approved tag restrictions.
- Python tests: **102 passed**, including provider validation and recruitment automation.
- Recruitment data validation, static link/metadata audit and syntax checks passed.
- No government listing data or publication workflow was changed.
- Test scripts use a stub browser and never contact the advertising provider, click ads, or generate artificial ad impressions.

Actual ad serving has **not** been verified: advertising is disabled and the new build cannot deploy to Netlify yet. No revenue has been claimed.

## Release steps after the hosting blocker is resolved

1. Recheck the website and unit statuses in the authenticated Adsterra account, content exclusions and any provider ads.txt requirements.
2. Review the updated privacy/consent experience on the production domain.
3. In `data/ads-config.json`, set `enabled` to `true` and `provider` to `adsterra`, leaving the verified native code, empty Google IDs and required versioned consent intact.
4. Run the build and checks, publish `dist` through the existing GitHub-to-Netlify connection, then verify the actual deployed revision and consent-gated rendering without clicking ads.
5. Enter payout, identity, tax or legal-verification data only directly in the provider account. Do not store such documents or private values in this repository.

## Official references

- https://adsterra.com/publishers-terms-managed/
- https://adsterra.com/privacy-policy-managed/
- https://adsterra.com/cookies/
- https://adsterra.com/blog/turn-a-profit-with-native-banners/
- https://adsterra.com/blog/set-up-publishers-dashboard/

## Paused Google path

The owner chose Adsterra instead of continuing Google AdSense. Before that change, Google's existing-account upgrade accepted the JOBPATH INDIA Netlify address and opened onboarding; **Connect your site** remained required. Google verification/review was not completed and no live Google ads were enabled. See `ADSENSE_MONETIZATION_SETUP.md` for that checkpoint.
