#!/usr/bin/env python3
"""Publish newly detected official recruitment *notice links* without human review.

This is source-attributed notice discovery, NOT verified job publication.
The public file is separate from data/jobs.json; no application URLs, dates,
vacancy counts, fees, or verified/open claims are generated.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlparse, unquote

from discover_notice_leads import normalized_url
from validate_review_queue import validate_review_queue

ROOT = Path(__file__).resolve().parents[1]
SOURCES_FILE = ROOT / "data/sources.json"
QUEUE_FILE = ROOT / "data/notice-review-queue.json"
JOBS_FILE = ROOT / "data/jobs.json"
PUBLIC_FILE = ROOT / "data/auto-notices.json"

# Only monitored, official organizational source domains are supported.
ALLOWED_SOURCE_IDS = frozenset(("sbi", "cwc", "kvs"))
MAX_ITEMS = 60
MAX_AGE_DAYS = 45
# Do not call generic site navigation, exam results or appointments "jobs".
EXCLUDED_TERMS = re.compile(
    r"\b(?:result(?:s)?|answer[\s-]?key|admit[\s-]?card|interview[\s-]?result|"
    r"merit[\s-]?list|selected[\s-]?candidate|tender|auction|"
    r"bid[\s-]?notice|corrigendum[\s-]?only)\b", re.I
)
RECRUITMENT_TERMS = re.compile(
    r"\b(?:recruitment|vacanc(?:y|ies)|advertisement|advt|hiring|"
    r"application[s]? for|appointment[s]? of|notification|engagement of consultant)\b", re.I
)


def is_date(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def canonical_document_key(url: str) -> tuple[str, str]:
    """Match www, URL-encoded spaces and case variants of the same PDF."""
    parsed = urlparse(url)
    return ((parsed.hostname or "").lower().removeprefix("www."),
            unquote(parsed.path).casefold())


def safe_notice_title(label: str, url: str) -> str | None:
    """Replace non-descriptive anchors using only the official PDF filename."""
    title = " ".join(label.strip().split())
    if title.casefold() in {"click here", "download", "view", "read more",
                            "important notice", "notice", "download pdf"}:
        filename = unquote(urlparse(url).path.rsplit("/", 1)[-1])
        if not filename.lower().endswith(".pdf"):
            return None
        stem = filename[:-4]
        stem = re.sub(r"^\d{1,4}_", "", stem)
        stem = re.sub(r"_[0-9a-f-]{18,}$", "", stem, flags=re.I)
        title = " ".join(stem.replace("_", " ").replace("-", " ").split())
    if len(title) < 12 or len(title) > 160:
        return None
    if not RECRUITMENT_TERMS.search(title) or EXCLUDED_TERMS.search(title):
        return None
    if re.search(r"[\x00-\x1f\x7f]", title):
        return None
    return title


def build_public_feed(queue: dict, sources: list[dict], jobs: list[dict], today: date):
    errors = validate_review_queue(queue, sources)
    if errors:
        raise ValueError("Invalid review queue: " + "; ".join(errors[:5]))
    by_id = {source["id"]: source for source in sources}
    already_published = {canonical_document_key(job["notificationUrl"]) for job in jobs
                         if job.get("verified") is True and job.get("isDemo") is False
                         and isinstance(job.get("notificationUrl"), str)}
    seen_urls = set()
    notices = []
    for lead in queue["leads"]:
        source_id = lead.get("source_id")
        if source_id not in ALLOWED_SOURCE_IDS:
            continue
        if lead.get("status") == "rejected":
            continue
        source = by_id.get(source_id)
        if not source:
            continue
        link = lead.get("notice_url", "")
        title = safe_notice_title(str(lead.get("title") or ""), link)
        first_seen = is_date(lead.get("first_seen"))
        if not first_seen or not (today - timedelta(days=MAX_AGE_DAYS) <= first_seen <= today):
            continue
        if (not isinstance(link, str) or normalized_url(source["url"], link) != link
                or canonical_document_key(link) in seen_urls
                or canonical_document_key(link) in already_published or not title):
            continue
        seen_urls.add(canonical_document_key(link))
        notices.append({
            "id": lead["id"],
            "title": title,
            "organization": source["name"],
            "source_id": source_id,
            "noticeUrl": link,
            "detectedDate": first_seen.isoformat(),
            "verificationStatus": "automatically_detected_unverified",
            "applicationStatus": "unknown",
        })
    notices.sort(key=lambda item: (item["detectedDate"], item["id"]), reverse=True)
    return {"version": 1, "notices": notices[:MAX_ITEMS]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if public feed is outdated")
    args = parser.parse_args()
    queue = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
    sources = json.loads(SOURCES_FILE.read_text(encoding="utf-8"))
    jobs = json.loads(JOBS_FILE.read_text(encoding="utf-8"))
    feed = build_public_feed(queue, sources, jobs, date.today())
    output = json.dumps(feed, ensure_ascii=False, indent=2) + "\n"
    current = PUBLIC_FILE.read_text(encoding="utf-8") if PUBLIC_FILE.exists() else ""
    if args.check:
        if current != output:
            print("Public auto-notice feed is not synchronized with source queue", file=sys.stderr)
            return 1
    elif current != output:
        PUBLIC_FILE.write_text(output, encoding="utf-8")
    print(f"Automatic public notices: {len(feed['notices'])}; all marked UNVERIFIED, none added to jobs.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
