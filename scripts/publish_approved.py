#!/usr/bin/env python3
"""Publish ONLY editor-approved, structurally verified official notices.

This is an approval-triggered autopublisher, not an AI fact-checker.
It NEVER promotes detected links or PDF text to a verified vacancy.
Unreviewed / incomplete / ambiguous records remain outside public jobs.json.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlparse

from discover_notice_leads import normalized_url
from validate_review_queue import CHECKS, validate_review_queue

ROOT = Path(__file__).resolve().parents[1]
JOBS_PATH = ROOT / "data/jobs.json"
QUEUE_PATH = ROOT / "data/notice-review-queue.json"
SOURCES_PATH = ROOT / "data/sources.json"
LEDGER_PATH = ROOT / "data/auto-publish-ledger.json"
REPORT_PATH = ROOT / "reports/auto-publish-latest.md"

# Deliberately narrow at launch; these three recruitment sources have previously
# returned HTML responses in our monitored GitHub runner environment.
PUBLISH_SOURCE_IDS = frozenset(("sbi", "cwc", "kvs"))
APP_HOST_EXCEPTIONS = {
    # Off-site application handling requires explicit editor verification.
    # Only an issuing source can authorize an approved exception in this code.
    "cwc": frozenset(("ibpsreg.ibps.in",)),
}
REQUIRED_TEXT = ("id", "title", "organization", "type", "state", "qualification",
                 "department", "category", "sourceOrganization", "description")
QUALIFICATIONS = frozenset(("10th Pass", "12th Pass", "ITI", "Diploma", "Any Degree",
                           "B.Tech / Engineering", "Postgraduate", "Other"))
REVIEW_MAX_AGE_DAYS = 14
ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{4,79}$")


def same_or_subdomain(hostname: str, origin: str) -> bool:
    host = hostname.lower().removeprefix("www.")
    base = origin.lower().removeprefix("www.")
    return host == base or host.endswith("." + base)


def valid_date(value: object) -> date | None:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return None
    try:
        result = date.fromisoformat(value)
        return result if result.isoformat() == value else None
    except ValueError:
        return None


def check_approved_candidate(lead: dict, source: dict, today: date) -> tuple[dict | None, list[str]]:
    problems = []
    if lead.get("status") != "reviewed":
        return None, ["Lead is not human-reviewed"]
    checklist = lead.get("review_checklist", {})
    if not isinstance(checklist, dict) or any(checklist.get(key) is not True for key in CHECKS):
        problems.append("All manual verification checklist items must be true")
    reviewer = lead.get("reviewed_by", "")
    if not isinstance(reviewer, str) or len(reviewer.strip()) < 3:
        problems.append("Named human reviewer required")
    reviewed_at = valid_date(lead.get("reviewed_at"))
    if reviewed_at is None or not (today - timedelta(days=REVIEW_MAX_AGE_DAYS) <= reviewed_at <= today):
        problems.append("Human review must be dated within the last 14 days")
    if source.get("id") not in PUBLISH_SOURCE_IDS or source.get("id") != lead.get("source_id"):
        problems.append("Recruitment issuer is not in automatic publication allowlist")
    official_notice = lead.get("notice_url", "")
    if not isinstance(official_notice, str) or normalized_url(source["url"], official_notice) != official_notice:
        problems.append("Notification URL must be on original official source host")
    job = lead.get("approved_job")
    if not isinstance(job, dict):
        return None, problems + ["approved_job object with human-verified details required"]
    if job.get("verified") is not True or job.get("isDemo") is not False:
        problems.append("Only verified=true, isDemo=false jobs qualify")
    if job.get("status") not in ("open", "upcoming"):
        problems.append("Only open/upcoming approved jobs may be published")
    for key in REQUIRED_TEXT:
        value = job.get(key)
        if not isinstance(value, str) or not value.strip() or len(value) > 1000:
            problems.append(f"Missing or invalid {key}")
    if not isinstance(job.get("id"), str) or ID_PATTERN.fullmatch(job["id"]) is None:
        problems.append("Invalid or missing unique job ID")
    if job.get("qualification") not in QUALIFICATIONS:
        problems.append("Qualification category not supported by website")
    if not isinstance(job.get("vacancies"), int) or isinstance(job.get("vacancies"), bool) or not 1 <= job["vacancies"] <= 1_000_000:
        problems.append("Verified positive vacancy count required")
    start = valid_date(job.get("startDate"))
    end = valid_date(job.get("lastDate"))
    published = valid_date(job.get("publishedDate"))
    verified = valid_date(job.get("lastVerifiedDate"))
    if not all((start, end, published, verified)):
        problems.append("All four date fields must be valid ISO dates")
    else:
        if start > end or published > today or end < today:
            problems.append("Application dates inconsistent or the window is expired")
        if end > today + timedelta(days=366):
            problems.append("Future application window outside 1-year limit")
        if verified != reviewed_at:
            problems.append("lastVerifiedDate must equal reviewed_at")
        if job["status"] != ("upcoming" if start > today else "open"):
            problems.append("Application status must match verified dates")
    for age_key in ("minAge", "maxAge"):
        age = job.get(age_key)
        if age is not None and (not isinstance(age, int) or isinstance(age, bool) or age < 0 or age > 120):
            problems.append(f"Invalid {age_key}")
    lo, hi = job.get("minAge"), job.get("maxAge")
    if isinstance(lo, int) and isinstance(hi, int) and lo > hi:
        problems.append("Age limit range reversed")
    if job.get("notificationUrl") != official_notice:
        problems.append("Job notificationUrl must equal the manually reviewed official notice")
    application_url = job.get("applicationUrl", "")
    app_parts = urlparse(application_url) if isinstance(application_url, str) else None
    official_parts = urlparse(source["url"])
    if (app_parts is None or app_parts.scheme != "https" or not app_parts.hostname or
        app_parts.username or app_parts.password or app_parts.port not in (None, 443)):
        problems.append("Valid HTTPS application URL required")
    elif not same_or_subdomain(app_parts.hostname, official_parts.hostname):
        if app_parts.hostname.lower() not in APP_HOST_EXCEPTIONS.get(source["id"], ()):
            problems.append("Off-site application URL is not on authorized application host allowlist")
        elif lead.get("application_host_independently_verified") is not True:
            problems.append("Explicit human verification of authorized external application host required")
    if job.get("sourceOrganization") and source.get("name"):
        # Preserve editorial name while requiring an attributable, non-fictitious source.
        if job["sourceOrganization"].lower().startswith(("example", "fictional", "sample")):
            problems.append("Fictional or placeholder source prohibited")
    if job.get("description") and re.search(r"\b(?:demo only|fictional|lorem ipsum|sample record)\b", job["description"], re.I):
        problems.append("Placeholder job descriptions cannot be published")
    if problems:
        return None, problems
    # Copy only editorial public job fields: never leak reviewer or workflow metadata.
    permitted = {
        "id", "title", "organization", "type", "state", "qualification",
        "department", "category", "minAge", "maxAge", "vacancies", "payScale",
        "startDate", "lastDate", "publishedDate", "fees", "selectionProcess",
        "notificationUrl", "applicationUrl", "sourceOrganization",
        "lastVerifiedDate", "verified", "isDemo", "status", "description"
    }
    clean = {key: value for key, value in job.items() if key in permitted}
    return clean, []


def prepare_publication(queue: dict, published: list[dict], sources: list[dict],
                        ledger: dict, today: date) -> tuple[list[dict], dict, list[str], list[str]]:
    """Pure, safe-by-default: any invalid reviewed candidate blocks all publication."""
    errors = validate_review_queue(queue, sources)
    if errors:
        return published, ledger, [], errors
    source_map = {s["id"]: s for s in sources}
    published_ids = {j.get("id"): j for j in published}
    approved = []
    # Only human-reviewed leads with explicit structured data are candidates.
    for lead in queue.get("leads", []):
        if lead.get("status") != "reviewed":
            continue
        source = source_map.get(lead.get("source_id"))
        if not source:
            errors.append(f"Review lead {lead.get('id')}: unrecognized source")
            continue
        candidate, problems = check_approved_candidate(lead, source, today)
        if problems:
            errors.extend(f"Review lead {lead.get('id')}: {message}" for message in problems)
            continue
        current = published_ids.get(candidate["id"])
        if current:
            # Never overwrite an already published notice silently; corrections need editorial action.
            if current.get("notificationUrl") != candidate["notificationUrl"]:
                errors.append(f"Review lead {lead.get('id')}: existing job ID belongs to another notice")
            continue
        if any(item["job"]["id"] == candidate["id"] for item in approved):
            errors.append(f"Duplicate approved candidate id {candidate['id']}")
            continue
        approved.append({"lead_id": lead["id"], "job": candidate,
                         "reviewed_by": lead["reviewed_by"],
                         "reviewed_at": lead["reviewed_at"]})
    if errors:
        return published, ledger, [], errors
    if not approved:
        return published, ledger, [], []
    next_jobs = published + [entry["job"] for entry in approved]
    next_ledger = {"version": 1, "published": list(ledger.get("published", []))}
    next_ledger["published"].extend({
        "job_id": entry["job"]["id"], "source_lead_id": entry["lead_id"],
        "reviewed_by": entry["reviewed_by"], "reviewed_at": entry["reviewed_at"],
        "published_on": today.isoformat()
    } for entry in approved)
    return next_jobs, next_ledger, [entry["job"]["id"] for entry in approved], []


def main() -> int:
    today = date.today()
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    jobs = json.loads(JOBS_PATH.read_text(encoding="utf-8"))
    sources = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    next_jobs, next_ledger, added, errors = prepare_publication(queue, jobs, sources, ledger, today)
    if errors:
        print("AUTO PUBLICATION BLOCKED: \n" + "\n".join(errors), file=sys.stderr)
        return 1
    if not added:
        print("Auto-publisher active: no new human-approved official vacancies; public jobs unchanged.")
        return 0
    # Workflows run independent JS validity checks before committing changes.
    JOBS_PATH.write_text(json.dumps(next_jobs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    LEDGER_PATH.write_text(json.dumps(next_ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        "# JobPath India — Automatic publication audit\n\n"
        f"Publication day: {today.isoformat()}\n\n"
        "This run only released manually reviewed, structurally checked job records.\n"
        "Never assume an unread PDF has been verified.\n\n"
        + "\n".join(f"- Published reviewed record: {item}" for item in added) + "\n",
        encoding="utf-8"
    )
    print(f"Auto-publisher staged {len(added)} verified/approved records: {', '.join(added)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
