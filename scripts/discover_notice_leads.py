#!/usr/bin/env python3
"""Find official recruitment-notice links for human review, without publishing jobs."""
from __future__ import annotations

import hashlib
import html
import json
import os
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urldefrag, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SOURCES_FILE = ROOT / "data" / "sources.json"
JOBS_FILE = ROOT / "data" / "jobs.json"
QUEUE_FILE = ROOT / "data" / "notice-review-queue.json"
REPORT_FILE = ROOT / "reports" / "notice-review-queue.md"

# Only selected sources previously reachable from the GitHub runner.
# CTET is an eligibility test, not a government vacancy listing.
SOURCE_IDS = ("sbi", "cwc", "kvs")
MAX_RESPONSE_BYTES = 400_000
MAX_LINKS_PER_SOURCE = 12
MAX_STORED_LINKS = 300
TIMEOUT_SECONDS = 12
NOTICE_TERMS = re.compile(
    r"(?:\brecruit(?:ment|ing)\b|\bvacanc(?:y|ies)\b|\badvertis(?:ement|e)\b|"
    r"\badvt\.?\b|\bnotification\b|\bselection\b|\bappointment\b|"
    r"\bposts?\b|\bopenings?\b|\bcareers?\b)", re.I)
DOC_SUFFIX = re.compile(r"\.(?:pdf|doc|docx)(?:$|[?])", re.I)
NOTICE_ID = re.compile(r"(?:\b20\d{2}\b|\b\d{1,3}/20\d{2}\b|\bcen[\s-]?\d)", re.I)


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.href = None
        self.text = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a" and self.href is None:
            self.href = dict(attrs).get("href")
            self.text = []

    def handle_data(self, data):
        if self.href is not None:
            self.text.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "a" and self.href is not None:
            self.links.append((self.href, " ".join(self.text)))
            self.href = None
            self.text = []


def normalized_url(base_url: str, href: str) -> str | None:
    if not isinstance(href, str) or len(href) > 2000:
        return None
    href = html.unescape(href.strip())
    if not href or any(char in href for char in ("\n", "\r", "\t")):
        return None
    base = urlparse(base_url)
    try:
        candidate = urlparse(urldefrag(urljoin(base_url, href)).url)
        if base.scheme != "https" or candidate.scheme != "https":
            return None
        if not base.hostname or not candidate.hostname:
            return None
        if candidate.username or candidate.password or candidate.port not in (None, 443):
            return None
        # Accept the issuing website and its subdomains only.
        base_host = base.hostname.lower().removeprefix("www.")
        host = candidate.hostname.lower().removeprefix("www.")
        if host != base_host and not host.endswith("." + base_host):
            return None
        return candidate.geturl()
    except ValueError:
        return None


def is_notice_link(label: str, url: str, source_url: str) -> bool:
    label = " ".join(html.unescape(label).split())[:180]
    parsed = urlparse(url)
    path = parsed.path.lower().rstrip("/")
    source_path = urlparse(source_url).path.lower().rstrip("/")
    if path == source_path and parsed.query == urlparse(source_url).query:
        return False
    if path in ("", "/", "/career", "/careers", "/recruitment", "/jobs", "/vacancies"):
        return False
    target = f"{label} {path}"
    if not NOTICE_TERMS.search(target):
        return False
    # Generic navigation is not a new notification.
    return bool(DOC_SUFFIX.search(url) or NOTICE_ID.search(target) or
                re.search(r"/(?:notification|advertisement|vacancy|recruitment)/[^/]{5,}", path))


def discover_from_html(source: dict, raw_html: str, existing_urls: set[str],
                       today: str) -> list[dict]:
    parser = LinkParser()
    parser.feed(raw_html)
    found = []
    local_seen = set()
    for href, label in parser.links:
        url = normalized_url(source["url"], href)
        if url is None or url in existing_urls or url in local_seen:
            continue
        if not is_notice_link(label, url, source["url"]):
            continue
        local_seen.add(url)
        title = " ".join(html.unescape(label).split())[:160] or "Official notification link (title not supplied)"
        fingerprint = hashlib.sha256(f'{source["id"]}|{url}'.encode()).hexdigest()[:20]
        found.append({
            "id": fingerprint,
            "source_id": source["id"],
            "source_name": source["name"],
            "source_page": source["url"],
            "title": title,
            "notice_url": url,
            "first_seen": today,
            "status": "needs_human_review",
            "review_checklist": {
                "original_notice_checked": False,
                "dates_checked": False,
                "vacancies_checked": False,
                "eligibility_checked": False,
                "application_link_checked": False
            }
        })
        if len(found) >= MAX_LINKS_PER_SOURCE:
            break
    return found


def fetch_page(url: str) -> str:
    request = Request(url, headers={
        "User-Agent": "JobPathIndiaSourceWatch/1.0 (+https://jobpath-india.netlify.app/)",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Encoding": "identity"
    })
    with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        if "html" not in response.headers.get("Content-Type", "").lower():
            raise ValueError("The source did not return HTML")
        raw = response.read(MAX_RESPONSE_BYTES + 1)
        return raw[:MAX_RESPONSE_BYTES].decode("utf-8", errors="replace")


def update_queue(sources: list[dict], previous: dict, published: list[dict],
                 fetcher, today: str) -> tuple[dict, list[tuple[str, str]]]:
    existing = previous.get("leads", [])
    if not isinstance(existing, list):
        raise ValueError("Expected review queue list")
    known_urls = {item.get("notice_url") for item in existing}
    known_urls.update(item.get("notificationUrl") for item in published)
    leads = list(existing)
    checks = []
    for source in sources:
        if source.get("id") not in SOURCE_IDS:
            continue
        try:
            page = fetcher(source["url"])
            candidates = discover_from_html(source, page, known_urls, today)
            candidates = candidates[:max(0, MAX_STORED_LINKS - len(leads))]
            leads.extend(candidates)
            known_urls.update(item["notice_url"] for item in candidates)
            checks.append((source["name"], f"{len(candidates)} new unverified link(s)"))
        except (HTTPError, URLError, TimeoutError, ValueError, OSError) as exc:
            checks.append((source["name"], f"could not inspect page ({type(exc).__name__})"))
    return {"version": 1, "leads": leads}, checks


def report_md(queue: dict) -> str:
    leads = queue.get("leads", [])
    pending = [item for item in leads if item.get("status") == "needs_human_review"]
    with_pdf = sum(bool(item.get("pdf_review")) for item in leads)
    out = [
        "# JobPath India — Notification review queue", "",
        "**NOT published jobs.** These are links discovered on known official source pages.",
        "A link does not establish a real vacancy, open application, deadline or eligibility.",
        f"**Total links:** {len(leads)} | **Awaiting review:** {len(pending)} | **PDFs examined:** {with_pdf}", "",
        "**PDF evidence below is unverified text, not structured job data.**", "",
        "Before publishing, check the original notice, issuing authority, post, vacancies,",
        "qualification, age, fees, notification number, dates, corrigenda and application link.", "",
        "| Organization | Link label | First seen | PDF text status | Review state | Source document |",
        "|---|---|---|---|---|---|"
    ]
    for item in pending:
        label = str(item["title"]).replace("|", " ").replace("\n", " ").replace("]", " ")
        org = str(item["source_name"]).replace("|", " ")
        pdf_data = item.get("pdf_review", {})
        pdf_status = str(pdf_data.get("status", "not_scanned")).replace("|", " ")
        out.append(f'| {org} | {label} | {item["first_seen"]} | {pdf_status} | Needs review | [Source link]({item["notice_url"]}) |')
    if not pending:
        out.append("| — | No pending official links detected yet | — | — | — | — |")
    evidence_leads = [item for item in pending if item.get("pdf_review", {}).get("evidence")]
    if evidence_leads:
        out += ["", "## Unverified excerpts from original PDFs", "",
                "These lines require checking the original layout, tables and any corrigenda.", ""]
        for item in evidence_leads[:20]:
            heading = html.escape(str(item["title"]).replace("\n", " "))[:130]
            out.append(f"### {heading}")
            for evidence in item["pdf_review"]["evidence"][:3]:
                snippet = html.escape(str(evidence.get("excerpt", ""))).replace("|", " ").replace("`", "'")
                out.append(f'- PDF page {evidence.get("page", "?")}: {snippet}')
            out.append("")
    out += [
        "", "**Safety:** Discovery does not edit the public jobs database.",
        "**Scope:** SBI, CWC and KVS HTML pages initially. Blocked websites, scripts and PDFs may be missed.", ""
    ]
    return "\n".join(out)


def main() -> int:
    today = datetime.now(timezone.utc).date().isoformat()
    sources = json.loads(SOURCES_FILE.read_text(encoding="utf-8"))
    published = json.loads(JOBS_FILE.read_text(encoding="utf-8"))
    prior = json.loads(QUEUE_FILE.read_text(encoding="utf-8")) if QUEUE_FILE.exists() else {"version": 1, "leads": []}
    queue, checks = update_queue(sources, prior, published, fetch_page, today)
    added = len(queue["leads"]) - len(prior.get("leads", []))
    if queue != prior or not QUEUE_FILE.exists():
        QUEUE_FILE.write_text(json.dumps(queue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = report_md(queue)
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not REPORT_FILE.exists() or REPORT_FILE.read_text(encoding="utf-8") != report:
        REPORT_FILE.write_text(report, encoding="utf-8")
    print(f"Notification review queue: {added} new unverified links; {len(queue['leads'])} total.")
    for name, result in checks:
        print(f"  {name}: {result}")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as output:
            output.write(f"\n## Notification link discovery\n\n{added} unverified links found. None published.\n")
            for name, result in checks:
                output.write(f"- {name}: {result}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
