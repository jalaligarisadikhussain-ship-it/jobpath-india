# JOBPATH INDIA — Fully automatic source-notice publication

This feature automatically publishes newly detected official recruitment **notice links** to the public website without waiting for a human reviewer. They remain clearly marked **AUTO-DETECTED · UNVERIFIED**. It never invents a post, vacancy count, education requirement, deadline, application URL or open/closed application status.

## Website display

- Homepage — recent automatic source notices
- Latest Jobs — automatic leads in a visibly separate section below verified jobs
- /auto-recruitment-notices/ — dedicated, public, noindex collection
- Recruitment Updates — automatic notice section
- Public JSON: /data/auto-notices.json

## Source checks

Daily at 07:45 IST (GitHub Actions schedule, subject to delay):

1. Monitor selected official recruiting organization pages.
2. Extract qualifying recruitment notice links from trusted sources.
3. Deduplicate against already verified recruitment notices.
4. Ignore results, merit lists and obviously unrelated navigation.
5. Validate source domain, dates and review-queue structure.
6. Build a limited public notice feed. Records expire from the feed 45 days after detection.
7. Commit the feed and trigger normal GitHub-to-Netlify deployment.

The initial supported organizations are SBI Careers, Central Warehousing Corporation and KVS. Other organizations may block automated access; source names do not imply active hiring.

## What is NOT automatic

- Determining whether a genuine vacancy exists inside a notice.
- Claiming an advertised position is open.
- Extracting and verifying application deadlines, vacancies, qualifications and fee categories.
- Correctly identifying every amendment, corrigendum or notice removed from an official website.
- Publishing a complete source-verified jobs.json entry without manual approval.

Existing human-approved auto-publishing remains separate and still requires explicit editorial approval before a structured vacancy is represented as verified.

## Operational files

- Source discovery: scripts/discover_notice_leads.py
- Unreviewed public lead generator: scripts/publish_detected_notices.py
- Human review queue: data/notice-review-queue.json (not deployed)
- Public notice feed: data/auto-notices.json
- Daily workflow: .github/workflows/daily-source-watch.yml
- Tests: tests/test_auto_notices.py and tests/final_features.test.mjs

No paid API is used. GitHub Actions and Netlify hosting remain subject to account free-tier limits. A successful workflow does not guarantee all official recruitment opportunities are discovered or that every detected link points to an active application.
