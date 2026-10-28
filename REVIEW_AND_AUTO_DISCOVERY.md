# JOBPATH INDIA — Automated notice discovery and human review

## What runs automatically

The existing daily GitHub Actions source-watch runs at **02:15 UTC / 07:45 IST**. It first monitors known recruitment organization pages for changes, then runs a separate, conservative link-discovery script. The first three selected HTML sources are SBI Careers, Central Warehousing Corporation Careers and KVS.

When an eligible same-site notification link is detected, it is added to the repository review queue:

- data/notice-review-queue.json — machine-readable candidates, with review checklist.
- reports/notice-review-queue.md — human-friendly review queue.
- data/source-watch-state.json and reports/source-watch-latest.md — source health and page-change signals.

These reports are **not deployed to the public Netlify website** by the explicit dist/ build allowlist. The reports may still be visible on GitHub if the repository is public.

## What this does NOT do

- It does not read or verify the full recruitment notice PDF.
- It does not infer posts, vacancy counts, eligibility, fees, start or end dates.
- It does not prove that the application window is open.
- It does not add entries to data/jobs.json or data/verified-jobs-2026-10-28.json.
- It does not submit applications, use CAPTCHA bypasses, or guarantee coverage of official websites.
- Blocked websites, JavaScript-rendered links and notices hosted on third-party domains can be missed.
- A source page, application link and notification link can be valid at different times.

## Phase 2: bounded PDF text evidence

The daily workflow now optionally downloads **at most three new official PDF links per day** from the selected sources after strict same-site redirect checking. Each PDF is limited to **4 MiB**, and text extraction examines **no more than 12 pages**. The free, pinned `pypdf` library runs on GitHub Actions, with no paid credits or API keys.

For each candidate, the repository review queue may hold:

- `pdf_review.status`: `needs_manual_verification`, `requires_ocr_or_manual_read`, `download_failed`, or `extraction_failed`.
- `pdf_review.evidence`: at most 12 short, page-numbered excerpts that mention recruitment or application terms.
- `pdf_review.page_count`, `pages_scanned`, and `checked_on` for provenance.
- `retry_after`: failed fetches are not retried daily; retry is deferred seven days.

These are **unverified excerpts**, not validated application deadlines or vacancy counts. Multi-column tables, image-only PDFs, missing pages, notices updated after download, and OCR-dependent scans remain manual verification cases. Report snippets are not proof of the underlying source's current meaning. The daily script never writes to the public jobs database.

The GitHub reviewer report is at `reports/notice-review-queue.md`. The raw review queue is in `data/notice-review-queue.json`. Neither is included in the static Netlify `dist/` output.

## Human review and safe publication

1. Open the latest review report on GitHub and follow a pending link to its official issuing website.
2. Open the actual advertisement and check any corrigenda. Confirm organization, advertisement number, post, vacancy count, qualifications, age cutoffs, fees, dates, application URL, and original source.
3. If it is invalid, mark the lead rejected and add a rejection_reason.
4. If fully verified, set every review_checklist field to true, change status to reviewed, add reviewed_by and reviewed_at in ISO YYYY-MM-DD format. This **only records review**; it does not publish.
5. Separately create or revise the correct entry in data/jobs.json with actual details and original notice, using an existing real record as a schema example. Do not mark a tentative or unclear notice as an open vacancy.
6. Commit through a pull request where practical. GitHub quality checks run automatically for data/jobs.json and the review queue, using Python unit tests, npm tests, and the existing recruitment data validator. After an approved commit reaches main, Netlify redeploys automatically.

## Local checks (optional)

Run these commands at the repository root:

    python3 -m pip install -r requirements-pdf.txt
    python3 -m unittest discover -s tests -p 'test_*.py'
    python3 scripts/validate_review_queue.py
    npm test
    npm run validate

No paid APIs, credits, scraping services or deploy tokens are required for the current system. GitHub Actions and Netlify account usage limits still apply.

## Current limitations and next development

Phase 1 and basic Phase 2 are implemented: notice-link detection, source-restricted PDF text snippets and human-review validation. Later phases should include source-specific PDF table parsing, multi-source evidence matching, explicit freshness thresholds, improved support for inaccessible pages, and a carefully controlled publishing gate. **Do not enable unattended public publication until those source-specific verifications are demonstrated with real notices and tests.**
