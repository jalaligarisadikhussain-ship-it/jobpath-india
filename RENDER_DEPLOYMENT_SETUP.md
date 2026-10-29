> **Status update — 29 October 2026:** Render Static Site `jobpath-india` deployed successfully at https://jobpath-india.onrender.com/ in `My Workspace`. Deployment `dep-dbhgj5ijnfac739v6lqg` is live and GA4 Realtime displayed one active user. Existing Netlify https://jobpath-india.netlify.app/ remains the Google-indexed primary. Follow-up SEO builds set Render page canonicals to Netlify and leave Render's sitemap empty to avoid proposing two URLs for the same content. Switching primary later requires updating `JOBPATH_PRIMARY_SEARCH_URL`, Search Console, and redirecting the former URL when available. Cost was $0.00 at the user-supplied billing screenshot; continued free use depends on usage limits.

# JOBPATH INDIA — Render Static Site preparation

Updated 29 October 2026. The owner authorized a separate Render Static Site in
the existing **My Workspace**. This document records preparation, not a successful
deployment. No Render service or live ad activation has been created by this work.

## Prepared service configuration

| Setting | Value |
| --- | --- |
| Service type | Static Site (global CDN; no web-service runtime or database) |
| Requested name | `jobpath-india` (actual returned URL must be checked) |
| Repository | `https://github.com/jalaligarisadikhussain-ship-it/jobpath-india` |
| Branch | `main` |
| Build command | `python3 scripts/build_dist.py` |
| Publish directory | `dist` |
| Auto-deploy | On commit, with the connected GitHub provider |
| Optional environment setting | `SKIP_INSTALL_DEPS=true`; the static build uses Python's standard library |

Use the existing authenticated GitHub connection, not an unauthenticated public
repository deployment that lacks automatic updates. Confirm the repo connection
and an automatic deploy after a later source change before claiming continuous
publication works. Existing government job data and scheduled publishing workflows
remain in this repository without modification.

## Build origins and existing Netlify site

`scripts/site_config.py` chooses the public origin in this order:

1. Explicit `JOBPATH_SITE_URL`, for a verified custom domain when one exists.
2. Render's documented `RENDER_EXTERNAL_URL` when `RENDER=true`.
3. Existing `https://jobpath-india.netlify.app` for Netlify and ordinary local builds.

Only HTTPS origins without credentials, ports, paths, queries or fragments are
accepted. The selected origin applies to all canonical URLs, Open Graph URLs,
structured data, sitemap entries and the robots sitemap directive. Do not run the
older `configure-domain.mjs` helper to prepare this deployment.

No Netlify project, hosting plan, government listing data, notice-feed state or
scheduled publication workflow was changed. The quality workflow also watches
the new hostname-configuration module. Source updates still require available
Netlify deployment credits to appear on that host.

## Cost checkpoint and current blocker

Render's Static Site product has no service subscription charge, but outbound
bandwidth and pipeline minutes count against workspace-level included usage.
Additional usage can incur charges. Current allowance, payment/overage behavior and
build spend settings must be inspected before deploying under the owner's ₹0 budget.

The Render connector can access the intended workspace and its existing services
but does not expose the billing allowance needed for that check. The dashboard
requires sign-in. The allowance and payment/overage settings remain unverified,
and no service has been created. Do not change existing games or other projects
to make room.

## Validation completed

- 107 Python tests and 41 JavaScript tests passed.
- Full builds cover all 39 routes and 25 sitemap entries for both the existing
  Netlify origin and a separate Render-style build origin without network access.
- Canonical, Open Graph and structured-data URLs, robots metadata, exact public
  feed preservation and disabled advertising were checked in both builds.
- Static route/metadata audit, data validation and advertising validation passed.
- Government job data and all automatic publication workflows are unchanged.

## Advertising release after hosting is available

The existing Adsterra website and NativeBanner_1 approval apply only to
`jobpath-india.netlify.app`. All ads remain disabled, and the current runtime's
approved-host restriction continues to reject any Render hostname.

After Render supplies a working production URL:

1. Verify all 39 routes, 25 sitemap entries, public data feeds and production commit.
2. Register that exact URL as its own website in the existing Adsterra account.
3. Confirm genuine website approval, native-unit activation, supplied tag, content
   exclusions and any applicable provider-supplied ads.txt instructions.
4. Update the validator, browser host restriction, exact identifiers and tests for
   the approved Render property. Never reuse the Netlify tag on another hostname.
5. Review hosting and advertising privacy disclosures and opt-in choices.
6. Enable only the approved native placement, deploy, and verify actual serving
   without clicking advertisements or generating artificial traffic.

The Google AdSense path remains paused. No approval or earnings is implied by
preparing or deploying a static website.

## References verified

- https://render.com/docs/static-sites
- https://render.com/docs/free
- https://render.com/docs/deploys
- https://render.com/docs/environment-variables
