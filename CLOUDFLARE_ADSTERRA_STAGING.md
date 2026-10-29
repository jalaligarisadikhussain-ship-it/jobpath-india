# Cloudflare Adsterra native banner — staging only

Website: https://jobpath-india.pages.dev/

Account-supplied native tag (29 Oct 2026):

```html
<script async="async" data-cfasync="false" src="https://bauval.org/21/84de856c9d01a37c08d4912fbf3df530"></script>
<div id="container-84de856c9d01a37c08d4912fbf3df530"></div>
```

## Safeguards staged

- `cloudflare-adsterra-prep` is a **non-production** branch; `main` is intentionally untouched, so Netlify, Render, and Cloudflare production are not changed by this work.
- This branch pins the exact account-provided URL and DOM container and restricts requests to `jobpath-india.pages.dev`; it does not reuse the Netlify unit.
- Native ads can only load after explicit visitor opt-in. Consent refusals, storage errors, and Global Privacy Control are respected; ad links stay outside recruitment application actions.
- `data/ads-config.json` has `enabled: false` and `provider: none`. The Cloudflare ad unit was reported Active by the owner, but website-level approval and gambling/betting campaign exclusion remain unverified, so `siteStatus` is conservatively `pending`.
- No ad impressions, clicks, income, or network response has been tested or claimed.

## Before any release

1. Confirm website-specific approval and exact unit ownership in Adsterra for `jobpath-india.pages.dev`.
2. Obtain a written assurance or available publisher-side filter excluding gambling/betting, and keep adult ads OFF; do not assume adult-off excludes gambling.
3. Review ongoing Google AdSense site review and privacy rules before mixing ad networks.
4. **Do not merge this branch directly into `main`**: it replaces the original Netlify-only ad configuration for staging. Production requires a host-specific integration that preserves existing Netlify and Render behavior and keeps GitHub automations on `main`.
5. Run JS and Python tests, SEO/site audit, and actual browser consent tests before enabling the exact tag on Cloudflare.
6. Only then set `enabled: true`, `provider: adsterra`, and `siteStatus: approved` for the Cloudflare-specific release, test without clicking ads or generating artificial traffic.

No payment, publisher identity documents, or keys should be stored in source control.
