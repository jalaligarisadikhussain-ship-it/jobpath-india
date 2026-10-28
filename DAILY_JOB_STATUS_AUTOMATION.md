# JOBPATH INDIA — Automated vacancy status maintenance

## Enabled workflow

The GitHub Actions workflow `.github/workflows/daily-job-status.yml` runs daily at **02:35 UTC / 08:05 IST** (subject to GitHub scheduled-run delays). It evaluates application date fields already stored in `data/jobs.json` and makes **time-only** state changes:

- `upcoming` → `open` when the reviewed start date arrives.
- `open` or `upcoming` → `closed` beginning the **day after** the reviewed last application date.
- `open` → `upcoming` if the recorded application start date is still in the future.
- A manually `closed` record is not automatically reopened.
- Unverified and demo entries are never changed.

The full previously checked job record, source link, and original `lastVerifiedDate` are preserved. Status maintenance is **not a fresh source verification**. If a government organization extends a deadline or publishes corrigenda, a human must update the verified dates after checking the original authority.

## Publishing

The script `scripts/sync_job_status.py` performs the pure date update and only writes `data/jobs.json` and `reports/jobs-status-audit.md` if changes exist. It does not create new jobs, remove jobs, change application links or change fees. On a real change, GitHub commits the data. Existing Netlify CI then builds and deploys the updated source.

The separate notice link detection remains at **07:45 IST**. The separate, human-reviewed structured job autopublisher remains at **07:55 IST**. This job status process runs at **08:05 IST**.

## Test commands

```bash
python3 scripts/sync_job_status.py --check
python3 -m unittest discover -s tests -p 'test_job_status_sync.py' -v
python3 scripts/build_dist.py
npm run validate
npm test
```

The `--check` option reports pending changes without modifying files. No paid API or credits are needed for this scheduled job. Existing hosting and GitHub Actions account limits still apply.

## PDF notice parsing improvements

The official-source PDF extractor now URL-encodes whitespace in PDF paths before HTTP requests, rejects cross-site redirect destinations, preserves size/page limits, and retries older `extraction_failed` records after a controlled cooldown. Any extracted PDF text is still marked unverified and not automatically converted into an active government job.
