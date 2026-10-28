#!/usr/bin/env python3
"""Update time-based display states of ALREADY verified jobs, never fabricate new jobs.

Date transitions are based solely on the latest human-verified application
dates recorded in jobs.json. This cannot detect notice corrigenda or extensions.
"""
from __future__ import annotations

import argparse
import json
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
JOBS_FILE = ROOT / "data" / "jobs.json"
AUDIT_FILE = ROOT / "reports" / "jobs-status-audit.md"


def sync_status(jobs: list[dict], today: date) -> tuple[list[dict], list[dict]]:
    """Pure update: retain every record and all reviewed fields."""
    updated = []
    changes = []
    for item in jobs:
        job = dict(item)
        if job.get("verified") is True and job.get("isDemo") is False:
            start = job.get("startDate")
            end = job.get("lastDate")
            if isinstance(start, str) and isinstance(end, str):
                try:
                    begin = date.fromisoformat(start)
                    deadline = date.fromisoformat(end)
                    if begin.isoformat() != start or deadline.isoformat() != end:
                        raise ValueError("not ISO")
                except ValueError:
                    pass
                else:
                    current = job.get("status")
                    # Preserve deliberate closures. Never automatically reopen
                    # a closed listing without a new verified corrigendum.
                    if current in ("open", "upcoming"):
                        target = "closed" if deadline < today else (
                            "upcoming" if begin > today else "open"
                        )
                        if target != current:
                            job["status"] = target
                            changes.append({
                                "id": job["id"],
                                "from": current,
                                "to": target,
                                "date": today.isoformat(),
                                "recorded_deadline": end,
                            })
        updated.append(job)
    return updated, changes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true",
                        help="Report pending date transitions without writing files")
    args = parser.parse_args()
    today = datetime.now(ZoneInfo("Asia/Kolkata")).date()
    jobs = json.loads(JOBS_FILE.read_text(encoding="utf-8"))
    updated, changes = sync_status(jobs, today)
    print(f"Checked {len(jobs)} records at IST date {today}; {len(changes)} status transitions.")
    if changes:
        for entry in changes:
            print(f"  {entry['id']}: {entry['from']} -> {entry['to']} (recorded deadline {entry['recorded_deadline']})")
    if args.check or not changes:
        return 0
    JOBS_FILE.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# JobPath India — Automatic job status transitions", "",
        f"Date evaluated: {today.isoformat()} (India Standard Time)", "",
        "Status follows the **previously recorded verified dates**, not a live recheck of the authority.",
        "Original notice, later corrigenda, application extensions and closures must be verified separately.", "",
        "| Job ID | Previous | Current | Previously verified deadline |",
        "|---|---|---|---|",
    ]
    for entry in changes:
        lines.append(f"| {entry['id']} | {entry['from']} | {entry['to']} | {entry['recorded_deadline']} |")
    AUDIT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
