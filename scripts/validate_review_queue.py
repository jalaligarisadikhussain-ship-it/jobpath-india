#!/usr/bin/env python3
"""Validate detected leads; the validator never promotes them to public jobs."""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

from discover_notice_leads import normalized_url

ROOT = Path(__file__).resolve().parents[1]
CHECKS = ("original_notice_checked", "dates_checked", "vacancies_checked",
          "eligibility_checked", "application_link_checked")
STATES = ("needs_human_review", "reviewed", "rejected")


def validate_review_queue(queue: dict, sources: list[dict]) -> list[str]:
    errors = []
    if queue.get("version") != 1 or not isinstance(queue.get("leads"), list):
        return ["Expected version 1 review queue with leads array"]
    known_sources = {item["id"]: item for item in sources}
    seen_ids, seen_urls = set(), set()
    for i, item in enumerate(queue["leads"]):
        ref = f"Lead {i+1}"
        if not isinstance(item, dict):
            errors.append(f"{ref}: expected JSON object")
            continue
        lead_id = item.get("id")
        source = known_sources.get(item.get("source_id"))
        link = item.get("notice_url")
        if not isinstance(lead_id, str) or not lead_id:
            errors.append(f"{ref}: missing id")
        elif lead_id in seen_ids:
            errors.append(f"{ref}: repeated id")
        seen_ids.add(lead_id)
        if source is None:
            errors.append(f"{ref}: unknown source")
        else:
            if item.get("source_page") != source["url"]:
                errors.append(f"{ref}: source page mismatch")
            if not isinstance(link, str) or normalized_url(source["url"], link) != link:
                errors.append(f"{ref}: link is not on official source host")
        if not isinstance(link, str) or link in seen_urls:
            errors.append(f"{ref}: duplicate or invalid link")
        seen_urls.add(link)
        title = item.get("title")
        if not isinstance(title, str) or not title.strip() or len(title) > 160:
            errors.append(f"{ref}: invalid title")
        try:
            date.fromisoformat(item.get("first_seen", ""))
        except (TypeError, ValueError):
            errors.append(f"{ref}: invalid first_seen date")
        state = item.get("status")
        if state not in STATES:
            errors.append(f"{ref}: unsupported review state")
        checklist = item.get("review_checklist")
        if not isinstance(checklist, dict) or any(not isinstance(checklist.get(field), bool) for field in CHECKS):
            errors.append(f"{ref}: incomplete review checklist")
            checklist = {}
        pdf_review = item.get("pdf_review")
        if pdf_review is not None:
            if not isinstance(pdf_review, dict):
                errors.append(f"{ref}: invalid PDF review metadata")
            else:
                pdf_status = pdf_review.get("status")
                allowed_pdf_states = ("needs_manual_verification",
                                      "requires_ocr_or_manual_read",
                                      "download_failed", "extraction_failed")
                if pdf_status not in allowed_pdf_states:
                    errors.append(f"{ref}: unsupported PDF review status")
                try:
                    date.fromisoformat(pdf_review.get("checked_on", ""))
                except (TypeError, ValueError):
                    errors.append(f"{ref}: invalid PDF checked_on date")
                evidence = pdf_review.get("evidence", [])
                if not isinstance(evidence, list) or len(evidence) > 12:
                    errors.append(f"{ref}: invalid PDF evidence list")
                else:
                    for evidence_item in evidence:
                        if (not isinstance(evidence_item, dict) or
                            not isinstance(evidence_item.get("page"), int) or
                            evidence_item["page"] < 1 or
                            not isinstance(evidence_item.get("excerpt"), str) or
                            len(evidence_item["excerpt"]) > 230):
                            errors.append(f"{ref}: invalid PDF evidence excerpt")
                            break
                if pdf_status == "download_failed":
                    try:
                        date.fromisoformat(pdf_review.get("retry_after", ""))
                    except (TypeError, ValueError):
                        errors.append(f"{ref}: retry_after required for failed PDF fetch")
        if state == "reviewed":
            if any(checklist.get(field) is not True for field in CHECKS):
                errors.append(f"{ref}: review must pass every checklist item")
            if not isinstance(item.get("reviewed_by"), str) or not item["reviewed_by"].strip():
                errors.append(f"{ref}: reviewed_by required")
            try:
                date.fromisoformat(item.get("reviewed_at", ""))
            except (TypeError, ValueError):
                errors.append(f"{ref}: reviewed_at date required")
        if state == "rejected" and not str(item.get("rejection_reason", "")).strip():
            errors.append(f"{ref}: rejection_reason required")
    return errors


def main() -> int:
    queue = json.loads((ROOT / "data" / "notice-review-queue.json").read_text(encoding="utf-8"))
    sources = json.loads((ROOT / "data" / "sources.json").read_text(encoding="utf-8"))
    errors = validate_review_queue(queue, sources)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"PASS: {len(queue['leads'])} notification links valid; no automatic job publication")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
