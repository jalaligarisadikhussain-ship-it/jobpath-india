#!/usr/bin/env python3
"""Daily, cautious change-detection for a curated list of recruitment sources.

This is NOT a vacancy scraper. It never modifies data/jobs.json or claims a
source-page change is an active or newly verified government recruitment.
One baseline is recorded at the first successful fetch; subsequent changed
fingerprints are flagged for human verification against original notices.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
SOURCE_PATH = ROOT / "data" / "sources.json"
STATE_PATH = ROOT / "data" / "source-watch-state.json"
REPORT_PATH = ROOT / "reports" / "source-watch-latest.md"
WATCH_IDS = (
    "ssc", "upsc", "rrb", "ibps", "sbi", "appsc", "tgpsc", "cwc",
    "national-insurance", "ctet", "kvs", "nvs", "employment-news",
)
MAX_BYTES = 400_000
TIMEOUT_SECONDS = 12


def canonical_content(raw: bytes, content_type: str) -> bytes:
    """Ignore basic volatile scripts/markup; hashes remain only change signals."""
    if "pdf" in content_type.lower():
        return raw
    content = raw.decode("utf-8", errors="replace")
    content = re.sub(r"<!--.*?-->", " ", content, flags=re.S)
    content = re.sub(r"<(script|style|noscript)\b[^>]*>.*?</\1\s*>", " ", content, flags=re.I | re.S)
    content = re.sub(r"<[^>]+>", " ", content)
    content = html.unescape(content)
    content = re.sub(r"\s+", " ", content).strip().lower()
    return content.encode("utf-8")


def fetch_fingerprint(url: str):
    if urlparse(url).scheme != "https":
        raise ValueError("Only HTTPS monitoring targets allowed")
    request = Request(url, headers={
        "User-Agent": "JobPathIndiaSourceWatch/1.0 (+https://jobpath-india.netlify.app/)",
        "Accept": "text/html,application/xhtml+xml,application/pdf;q=0.8,*/*;q=0.5",
        "Accept-Encoding": "identity",
    })
    with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        content_type = response.headers.get("Content-Type", "text/html")
        if not any(kind in content_type.lower() for kind in ("html", "text/plain", "pdf")):
            raise ValueError(f"Unsupported response type: {content_type[:75]}")
        data = response.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            data = data[:MAX_BYTES]
        normalized = canonical_content(data, content_type)
        if len(normalized) < 80:
            raise ValueError("Response too short for a meaningful change check")
        return hashlib.sha256(normalized).hexdigest()


def describe_fetch_failure(exc: Exception) -> str:
    """Stable diagnostics; never confuse inaccessible sources with closed jobs."""
    if isinstance(exc, HTTPError):
        return f"HTTP {exc.code} (remote server blocked or rejected request)"
    if isinstance(exc, URLError):
        return f"network/DNS/TLS error ({type(getattr(exc, 'reason', None)).__name__})"
    if isinstance(exc, TimeoutError):
        return "request timed out"
    if isinstance(exc, ValueError):
        message = str(exc)
        if message.startswith("Unsupported response type:"):
            return "unsupported website response type"
        if "too short" in message:
            return "unexpectedly short website response"
        return "invalid website response"
    return f"local I/O error ({type(exc).__name__})"


def monitor_sources(sources, previous, fetcher, today):
    """Return (new_state, observations), no network access inside this function."""
    old_entries = previous.get("sources", {})
    result = {"version": 1, "sources": dict(old_entries)}
    observations = []
    for src in sources:
        if src.get("id") not in WATCH_IDS:
            continue
        sid = src["id"]
        existing = old_entries.get(sid, {})
        entry = dict(existing)
        url = src.get("url", "")
        kind = "unchanged"
        try:
            digest = fetcher(url)
            old_digest = existing.get("fingerprint")
            if old_digest is None:
                kind = "baseline"
            elif old_digest != digest:
                kind = "possible_change"
            elif existing.get("status") != "reachable":
                kind = "recovered"
            if kind != "unchanged":
                entry = {"name": src["name"], "url": url, "status": "reachable",
                         "fingerprint": digest, "last_change_or_status_date": today}
            # If unchanged, don't modify the file: avoids unnecessary daily deploys.
        except (URLError, HTTPError, TimeoutError, ValueError, OSError) as exc:
            note = f"Could not check: {describe_fetch_failure(exc)}; not proof of a closed recruitment"
            changed = (existing.get("status") != "unreachable"
                       or existing.get("note") != note or existing.get("url") != url)
            kind = "unreachable" if changed else "unchanged_unreachable"
            if changed:
                entry = {"name": src["name"], "url": url, "status": "unreachable",
                         "fingerprint": existing.get("fingerprint"),
                         "last_change_or_status_date": today,
                         "note": note}
        result["sources"][sid] = entry
        observations.append((src["name"], kind, url))
    return result, observations


def report_markdown(state):
    output = ["# JobPath India — Recruitment source monitoring", "",
              "This is a **change-monitoring report**, not a list of verified new vacancies.",
              "Changes can be due to navigation, announcements, site redesigns or dynamic content.",
              "Before publishing a vacancy, a person must check its official notification PDF, dates, eligibility, vacancies and application link.", "",
              "| Source | Last observed state | Date of last material change | Source website |",
              "|---|---|---|---|"]
    for sid in WATCH_IDS:
        item = state.get("sources", {}).get(sid)
        if not item:
            continue
        url = item.get("url", "")
        name = item.get("name", sid).replace("|", " ")
        status = item.get("status", "unknown")
        date = item.get("last_change_or_status_date", "-")
        output.append(f"| {name} | {status} | {date} | [Visit source]({url}) |")
    output += ["", "**What this does not do:** read every PDF, verify all vacancies, update application eligibility, or publish new jobs automatically.",
               "**Monitoring caveat:** blocked sites are 'unreachable', not 'no recruitment'; content changes are leads for review, not confirmed jobs.", ""]
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", default=datetime.now(timezone.utc).date().isoformat())
    args = parser.parse_args()
    sources = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    previous = json.loads(STATE_PATH.read_text(encoding="utf-8")) if STATE_PATH.exists() else {"version": 1, "sources": {}}
    state, observations = monitor_sources(sources, previous, fetch_fingerprint, args.date)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(report_markdown(state), encoding="utf-8")
    counts = {kind: sum(1 for _, k, _ in observations if k == kind) for kind in
              ("possible_change", "baseline", "recovered", "unreachable", "unchanged", "unchanged_unreachable")}
    message = (f"Daily check {args.date} UTC — " + ", ".join(f"{k}: {v}" for k, v in counts.items()))
    print(message)
    for name, kind, url in observations:
        if kind != "unchanged":
            print(f"  {kind}: {name}: {url}")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as out:
            out.write("## JobPath India source watch\n\n" + message + "\n\n")
            out.write("Changes are **unverified leads only**, not automatically publishable vacancies.\n\n")
            for name, kind, url in observations:
                if kind in ("possible_change", "unreachable", "baseline"):
                    out.write(f"- **{kind}** — [{name}]({url})\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
