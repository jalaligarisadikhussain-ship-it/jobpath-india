# JobPath India — Six-Month Expert Upgrade Plan
**Window:** 2 November 2026–30 April 2027  
**Primary production:** https://jobpath-india.pages.dev/  
**Budget:** ₹0; keep Cloudflare Pages and existing approved integrations.

## Delivered foundations (2 November 2026)
- Verified-source recruitment database and per-record last-checked labels; no fabricated current vacancies.
- Daily scheduled static-site rebuild: `.github/workflows/publish-generated-pages.yml`. A past deadline automatically stops appearing in the homepage's open-notice fallback.
- Automated build/source/SEO tests: `.github/workflows/source-quality.yml`.
- Weekly source freshness, imminent-deadline and overdue-status dashboard in GitHub Actions: `.github/workflows/weekly-editorial-audit.yml`, `scripts/editorial-health.mjs`.
- Canonical URLs point to Cloudflare, not the historical Netlify deployment.

## Remaining release milestones
| Month | Delivery focus | Exit criterion |
| --- | --- | --- |
| Nov 2026 | Mobile QA, verify both Cloudflare deployments, audit live apply links and advertiser creatives | Tested on small/large phones; no incorrect hiring promises; risky creatives escalated to provider |
| Dec 2026 | Rewrite weak or repetitive category text, improve exam calendar and guide navigation | Original helpful pages, credible primary sources and working mobile menus |
| Jan 2027 | Better filtering, saved-job workflows and clear official-apply journey | Visitors can find, verify and bookmark roles without an account or forced ads |
| Feb 2027 | Search Console coverage, social previews, performance and accessible forms | Indexing issues documented; no invalid job-rich-result markup; fast core navigation |
| Mar 2027 | Compliance-first monetization and privacy review | Written advertiser category exclusions or publisher-controlled disabling of unsafe zones; consent requirements reviewed |
| Apr 2027 | Long-run stability and content audit | Six-month logs reviewed; stale notices corrected or removed; build/test and source publication continue reliably |

These are **planned releases**, not changes that run automatically. New features, research, official notice validation and mobile visual QA require separate work as each milestone arrives.

## Weekly publisher dashboard (real measurements only)
1. From GitHub Actions, inspect the latest `Weekly JobPath recruitment content health` report.
2. Review records nearing deadline within seven days and records whose source was last checked over fourteen days ago.
3. Compare Google Search Console clicks, index coverage, relevant queries and GA4 engagement against **actual measured baselines**; never assert visitors, growth or revenue without measurement.
4. Sample official notices for application status, fee, eligibility, advertisement number and corrigenda.
5. Log unsuitable ad screenshots with the network and ask for written zone-level exclusions.

## Quality and safety constraints
- No demo vacancy in a public live list, no artificial job openings, no guaranteed job/visa promises.
- No fabricated views, employers, reviews, citations, revenue or sponsorship claims.
- Any expired job must be clearly closed or absent from open listings. A GitHub check cannot itself verify a third-party official notice.
- Preserve existing ads and user privacy controls unless they become unsafe or noncompliant; advertiser category filtering depends on the provider.
- Preserve Cloudflare, Search Console verification, accessibility and source attribution on every release.
- Do not syndicate employer content or imply authorized partnerships without approval.

## Six-month maintenance cadence
Daily automated code/data build checks and Monday editorial reports are configured as GitHub Actions and depend on GitHub scheduling, permissions and free-tier availability. Human review is still needed for actual vacancy verification, source corrections, ad disputes and strategic releases.
