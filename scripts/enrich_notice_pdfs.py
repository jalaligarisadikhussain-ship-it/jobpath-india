#!/usr/bin/env python3
"""Bounded extraction of PDF notice *evidence* into a PRIVATE review queue.

Nothing in this script changes data/jobs.json or marks recruitment verified.
Machine extraction may be wrong. A human must read the original PDF, tables,
corrigenda, eligibility conditions and dates before publishing any vacancy.
"""
from __future__ import annotations

import io
import json
import os
import re
from datetime import date, timedelta, timezone, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

from discover_notice_leads import (
    JOBS_FILE, QUEUE_FILE, REPORT_FILE, SOURCES_FILE, normalized_url, report_md
)

MAX_PDF_BYTES = 4 * 1024 * 1024
MAX_PDF_PAGES = 12
MAX_EXCERPTS = 12
MAX_EXCERPT_CHARS = 230
MAX_PDFS_PER_RUN = 3
RETRY_DAYS = 7
TIMEOUT_SECONDS = 15
PDF_PATH = re.compile(r"\.pdf$", re.I)
EVIDENCE_TERMS = re.compile(
    r"(?:\bvacanc(?:y|ies)\b|\bpost(?:s)?\b|\bqualification(?:s)?\b|"
    r"\beligib(?:le|ility)\b|\bclosing date\b|\blast date\b|"
    r"\bapplication fee\b|\bage limit\b|\bonline application\b|"
    r"\bimportant dates\b|\badvertisement\b|\brecruitment\b|"
    r"\bnotification\b|\bpay scale\b|\bselection process\b)", re.I
)


def encoded_request_url(url: str) -> str:
    """Make official URLs with spaces safe for HTTP without changing the authority."""
    parsed = urlparse(url)
    path = quote(parsed.path, safe="/%:@!class SameSiteRedirectHandler(HTTPRedirectHandler):'()*+,;=-._~")
    query = quote(parsed.query, safe="/%:@!class SameSiteRedirectHandler(HTTPRedirectHandler):'()*+,;=?-._~")
    return parsed._replace(path=path, query=query).geturl()


class SameSiteRedirectHandler(HTTPRedirectHandler):
    """No redirect to a third-party, http, IP, or changed source host."""

    def __init__(self, source_url: str):
        super().__init__()
        self.source_url = source_url

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        target = normalized_url(self.source_url, newurl)
        if target is None:
            raise HTTPError(newurl, code, "Cross-site redirect blocked", headers, fp)
        return super().redirect_request(req, fp, code, msg, headers, encoded_request_url(target))


def download_official_pdf(url: str, source_url: str) -> bytes:
    if normalized_url(source_url, url) != url:
        raise ValueError("Document URL differs from trusted official source host")
    if not PDF_PATH.search(urlparse(url).path):
        raise ValueError("Not a direct PDF notice")
    opener = build_opener(SameSiteRedirectHandler(source_url))
    request = Request(encoded_request_url(url), headers={
        "User-Agent": "JobPathIndiaSourceWatch/1.0 (+https://jobpath-india.netlify.app/)",
        "Accept": "application/pdf,application/octet-stream;q=0.6",
        "Accept-Encoding": "identity",
    })
    with opener.open(request, timeout=TIMEOUT_SECONDS) as response:
        # Redirect handler validates every redirect before it can be followed.
        if normalized_url(source_url, response.geturl()) is None:
            raise ValueError("Untrusted document redirect")
        raw = response.read(MAX_PDF_BYTES + 1)
        if len(raw) > MAX_PDF_BYTES:
            raise ValueError("PDF exceeds size limit")
        if not raw.startswith(b"%PDF-"):
            raise ValueError("Document is not a PDF")
        return raw


def evidence_from_pages(pages: list[str]) -> list[dict]:
    """Preserve short page-numbered verbatim snippets; never infer numeric fields."""
    evidence, seen = [], set()
    for page_num, page in enumerate(pages, start=1):
        for raw_line in page.splitlines():
            line = " ".join(raw_line.split())
            if len(line) < 12 or not EVIDENCE_TERMS.search(line):
                continue
            excerpt = line[:MAX_EXCERPT_CHARS]
            key = excerpt.casefold()
            if key in seen:
                continue
            seen.add(key)
            evidence.append({"page": page_num, "excerpt": excerpt})
            if len(evidence) >= MAX_EXCERPTS:
                return evidence
    return evidence


def extract_pdf_evidence(pdf_bytes: bytes) -> dict:
    # Imported here so pure offline URL/queue tests can run independently.
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(pdf_bytes), strict=False)
    if reader.is_encrypted:
        raise ValueError("Password-protected PDF cannot be examined")
    total = len(reader.pages)
    if total < 1:
        raise ValueError("PDF contains no pages")
    read_pages = min(total, MAX_PDF_PAGES)
    text_by_page = []
    for index in range(read_pages):
        # Truncate immediately; PDF text extraction may be imperfect.
        text_by_page.append((reader.pages[index].extract_text() or "")[:30000])
    char_count = sum(len(text.strip()) for text in text_by_page)
    return {
        "status": "needs_manual_verification" if char_count >= 80 else "requires_ocr_or_manual_read",
        "page_count": total,
        "pages_scanned": read_pages,
        "text_characters": char_count,
        "method": "pypdf_text_only_no_ocr",
        "evidence": evidence_from_pages(text_by_page),
    }


def enrich_queue(queue: dict, sources: list[dict], downloader, extractor,
                 today: str, max_documents: int = MAX_PDFS_PER_RUN) -> tuple[dict, dict]:
    trusted = {source["id"]: source["url"] for source in sources}
    updated = {"version": 1, "leads": []}
    stats = {"examined": 0, "successful": 0, "failed": 0, "no_text": 0, "skipped": 0}
    for lead in queue.get("leads", []):
        item = dict(lead)
        source_url = trusted.get(item.get("source_id"))
        notice_url = item.get("notice_url", "")
        prior = item.get("pdf_review", {})
        prior_status = prior.get("status")
        if (item.get("status") != "needs_human_review" or
            not isinstance(notice_url, str) or not source_url or
            normalized_url(source_url, notice_url) != notice_url or
            not PDF_PATH.search(urlparse(notice_url).path) or
            (prior_status not in (None, "download_failed", "extraction_failed")) or
            (prior_status in ("download_failed", "extraction_failed")
             and prior.get("retry_after", "") > today) or
            stats["examined"] >= max_documents):
            stats["skipped"] += 1
            updated["leads"].append(item)
            continue
        stats["examined"] += 1
        try:
            raw_pdf = downloader(notice_url, source_url)
            result = extractor(raw_pdf)
            result["checked_on"] = today
            item["pdf_review"] = result
            if result["status"] == "needs_manual_verification":
                stats["successful"] += 1
            else:
                stats["no_text"] += 1
        except (HTTPError, URLError, TimeoutError, ValueError, OSError) as exc:
            # Store only error category, not remote content or stack traces.
            item["pdf_review"] = {
                "status": "download_failed",
                "checked_on": today,
                "retry_after": (date.fromisoformat(today) + timedelta(days=RETRY_DAYS)).isoformat(),
                "reason": type(exc).__name__
            }
            stats["failed"] += 1
        except Exception:
            # Malformed PDF/unsupported encryption may fail within the library.
            item["pdf_review"] = {
                "status": "extraction_failed",
                "checked_on": today,
                "reason": "PDFParsingError",
                "retry_after": (date.fromisoformat(today) + timedelta(days=RETRY_DAYS)).isoformat()
            }
            stats["failed"] += 1
        updated["leads"].append(item)
    return updated, stats


def main() -> int:
    today = datetime.now(timezone.utc).date().isoformat()
    queue = json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
    sources = json.loads(SOURCES_FILE.read_text(encoding="utf-8"))
    updated, stats = enrich_queue(queue, sources, download_official_pdf, extract_pdf_evidence, today)
    if updated != queue:
        QUEUE_FILE.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = report_md(updated)
    if not REPORT_FILE.exists() or REPORT_FILE.read_text(encoding="utf-8") != report:
        REPORT_FILE.write_text(report, encoding="utf-8")
    print(f"PDF evidence scan: {stats}. No jobs published.")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as out:
            out.write(f"\n## PDF evidence scan (not verified)\n\n{stats}\n\n")
            out.write("PDF text may be misleading or incomplete; review original notice.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
