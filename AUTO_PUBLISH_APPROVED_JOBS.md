# JOBPATH INDIA — Approved job auto-publishing (enabled)

## What is automatic now

After an editor has verified a real government recruitment notice and explicitly approved its full job record, GitHub Actions automatically copies the record to `data/jobs.json`, validates the website, commits the update, and triggers the existing GitHub-to-Netlify production deployment.

The publisher is configured for:
- `push` changes to `data/notice-review-queue.json` on `main` (to publish immediately after an editor approves a record).
- Daily scheduled run at **02:25 UTC / 07:55 IST** (backup for approvals or GitHub bot changes).
- Manual `workflow_dispatch` in GitHub Actions if a rerun is ever required.

This is **approval-triggered auto-publishing**, not unattended AI verification of arbitrary government PDFs.

## How a real opening is approved

1. Open `reports/notice-review-queue.md` on GitHub and open the issuing authority's notice and any corrigenda.
2. Independently verify the employer, post, advertised vacancy count, educational and age eligibility, fee categories, exact application start/end dates, advertisement number, and authorized application form.
3. Edit the matching record in `data/notice-review-queue.json`, and set:
   - `status`: `"reviewed"`
   - Each of the five `review_checklist` values: `true`
   - `reviewed_by`: name of the human reviewer
   - `reviewed_at`: current date in `YYYY-MM-DD` format
   - `auto_publish_approved`: `true`
   - `approved_job`: the complete checked job record, using the same field names and categories as existing real entries in `data/jobs.json`.
4. The `approved_job` object must have `verified: true`, `isDemo: false`, `lastVerifiedDate` equal to `reviewed_at`, the exact official notification URL matching the lead's `notice_url`, and a verified HTTPS application URL. The `status` must be `open` or `upcoming` consistently with verified dates.
5. If the application form is hosted outside the original organization website, it must be an explicitly supported domain. The currently configured CWC exception is `ibpsreg.ibps.in`. For this authorized host, the reviewer must also set `application_host_independently_verified: true` on the review lead, after checking the issuing body's advertisement.
6. Commit the review queue change to `main`. GitHub's **Publish human-approved recruitment jobs** workflow validates and publishes approved records; no manual `jobs.json` edit or ZIP upload is needed. Netlify deploys from GitHub automatically.

## Publication restrictions

- Source allowlist currently consists of **SBI Careers, CWC Careers and KVS**. Unlisted sources require explicit code/policy review before automatic publication.
- Human review must have occurred in the last **14 days** for a *new* publication.
- A candidate must have a verified positive vacancy count and full start/end dates; expired applications are not auto-published.
- Unknown or external application domains are rejected. Off-site host lookalikes and insecure HTTP URLs are rejected.
- The publication must have a unique job ID; a published record is never overwritten automatically. Revisions and corrections require separate editorial review.
- Detection, text extraction, and machine-generated snippets **cannot** mark a job verified.
- Any invalid explicitly approved candidate stops the entire batch; no partial publication is committed.
- Reviews that are merely `"reviewed"` but lack `auto_publish_approved: true` stay out of the public site.
- The public site automatically shows expired records as `closed` in browsers based on date.

## Tracking and testing

- Actions: `.github/workflows/auto-publish-approved-jobs.yml`
- Publisher: `scripts/publish_approved.py`
- Approval tests: `tests/test_publish_approved.py`
- Private audit in repository: `data/auto-publish-ledger.json`, `reports/auto-publish-latest.md`
- Public data: `data/jobs.json`, rendered by Netlify's `scripts/build_dist.py`
- Run checks: `python3 scripts/publish_approved.py` and `npm test && npm run validate`.
- No paid API, scraper credits, or premium subscription is required. GitHub Actions and Netlify free-tier usage restrictions apply.

**Important:** A successful GitHub workflow proves the automated *technical process* runs. It cannot independently establish that a job advertisement is current or correct, or that Netlify was updated without checking the published site. The publisher starts with an empty approved queue, so no new jobs have been auto-published until a real notice passes editor approval.
