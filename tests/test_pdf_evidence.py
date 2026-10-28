"""Offline tests for cautious PDF notice evidence processing."""
import sys
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import enrich_notice_pdfs as pdf

SOURCE = {"id": "cwc", "url": "https://cwceportal.com/careers", "name": "Central Warehousing Corporation"}
URL = "https://cwceportal.com/Careers/Guidelines/Recruitment2026.pdf"


def pending(url=URL):
    return {
        "id": "notice1",
        "source_id": "cwc",
        "source_name": SOURCE["name"],
        "source_page": SOURCE["url"],
        "notice_url": url,
        "title": "Recruitment 2026",
        "first_seen": "2026-10-28",
        "status": "needs_human_review",
        "review_checklist": {
            "original_notice_checked": False,
            "dates_checked": False,
            "vacancies_checked": False,
            "eligibility_checked": False,
            "application_link_checked": False
        }
    }


def fake_extract(data):
    return {"status": "needs_manual_verification", "method": "fixture",
            "evidence": [{"page": 1, "excerpt": "Last date 1 Nov 2026"}],
            "page_count": 1, "pages_scanned": 1, "text_characters": 100}


class PdfEvidenceTests(unittest.TestCase):
    def test_evidence_preserves_line_not_structured_verified_fields(self):
        result = pdf.evidence_from_pages(["Recruitment notice\nLast date for submitting application is 1 Nov 2026\nFor further details", "Eligibility required: degree"])
        self.assertEqual([x["page"] for x in result], [1, 1, 2])
        self.assertIn("Last date", result[1]["excerpt"])
        self.assertNotIn("lastDate", result[1])

    def test_regular_notice_requires_human_review_after_extraction(self):
        queue, stats = pdf.enrich_queue({"version": 1, "leads": [pending()]}, [SOURCE],
                                         lambda url, source: b"%PDF-fake", fake_extract, "2026-10-28")
        self.assertEqual(stats["successful"], 1)
        item = queue["leads"][0]
        self.assertEqual(item["status"], "needs_human_review")
        self.assertEqual(item["pdf_review"]["status"], "needs_manual_verification")
        self.assertFalse(any(item["review_checklist"].values()))
        self.assertNotIn("vacancies", item)
        self.assertNotIn("lastDate", item)

    def test_untrusted_host_never_downloaded(self):
        bad = pending("https://cwceportal.com.evil.invalid/Recruitment2026.pdf")
        def no_fetch(url, source):
            raise AssertionError("Off-site link must not be fetched")
        queue, stats = pdf.enrich_queue({"version": 1, "leads": [bad]}, [SOURCE], no_fetch,
                                         fake_extract, "2026-10-28")
        self.assertEqual(stats["examined"], 0)
        self.assertNotIn("pdf_review", queue["leads"][0])

    def test_html_notice_remains_for_manual_review(self):
        html = pending("https://cwceportal.com/Careers/Recruitment2026")
        queue, stats = pdf.enrich_queue({"version": 1, "leads": [html]}, [SOURCE],
                                         lambda *_: (_ for _ in ()).throw(AssertionError),
                                         fake_extract, "2026-10-28")
        self.assertEqual(stats["examined"], 0)
        self.assertEqual(queue["leads"][0]["status"], "needs_human_review")

    def test_already_approved_lead_never_fetched(self):
        lead = pending()
        lead["status"] = "reviewed"
        queue, stats = pdf.enrich_queue({"version": 1, "leads": [lead]}, [SOURCE],
                                         lambda *_: (_ for _ in ()).throw(AssertionError),
                                         fake_extract, "2026-10-28")
        self.assertEqual(stats["examined"], 0)

    def test_max_three_pdfs_per_daily_run(self):
        leads = [dict(pending(), id=str(i), notice_url=URL.replace("2026.pdf", f"{i}2026.pdf")) for i in range(5)]
        queue, stats = pdf.enrich_queue({"version": 1, "leads": leads}, [SOURCE],
                                         lambda *_: b"%PDF-fake", fake_extract, "2026-10-28")
        self.assertEqual(stats["examined"], 3)
        self.assertEqual(sum("pdf_review" in x for x in queue["leads"]), 3)

    def test_download_failure_retries_after_seven_days(self):
        def denied(url, source):
            raise HTTPError(url, 403, "Forbidden", None, None)
        first, stats = pdf.enrich_queue({"version": 1, "leads": [pending()]}, [SOURCE],
                                        denied, fake_extract, "2026-10-28")
        self.assertEqual(stats["failed"], 1)
        self.assertEqual(first["leads"][0]["pdf_review"]["retry_after"], "2026-11-04")
        second, stats = pdf.enrich_queue(first, [SOURCE],
                                         lambda *_: (_ for _ in ()).throw(AssertionError),
                                         fake_extract, "2026-10-29")
        self.assertEqual(stats["examined"], 0)
        self.assertEqual(first, second)
        third, stats = pdf.enrich_queue(first, [SOURCE], lambda *_: b"%PDF-fake",
                                        fake_extract, "2026-11-04")
        self.assertEqual(stats["successful"], 1)
        self.assertEqual(third["leads"][0]["pdf_review"]["checked_on"], "2026-11-04")

    def test_insufficient_extractable_text_flagged_for_review(self):
        queue, stats = pdf.enrich_queue({"version": 1, "leads": [pending()]}, [SOURCE],
                                         lambda *_: b"%PDF-fake",
                                         lambda _: {"status": "requires_ocr_or_manual_read", "evidence": []},
                                         "2026-10-28")
        self.assertEqual(stats["no_text"], 1)
        self.assertEqual(queue["leads"][0]["status"], "needs_human_review")

    def test_official_pdf_url_with_spaces_encoded_for_request(self):
        original = ("https://cwceportal.com/Careers/Guidelines/44/"
                    "44_Notice for Engagement of Consultant_abcd.pdf")
        result = pdf.encoded_request_url(original)
        self.assertIn("Notice%20for%20Engagement%20of%20Consultant", result)
        self.assertEqual(pdf.encoded_request_url(result), result)

    def test_pdf_redirect_keeps_same_site_with_spaces(self):
        handler = pdf.SameSiteRedirectHandler(SOURCE["url"])
        original = "https://cwceportal.com/Careers/Recruitment2026.pdf"
        request = handler.redirect_request(
            Request(original), None, 302, "redirect", {},
            "https://cwceportal.com/Careers/Guidelines/Notice 2026.pdf")
        self.assertIn("Notice%202026.pdf", request.full_url)

    def test_old_pdf_parsing_failures_get_one_retry(self):
        x = pending()
        x["pdf_review"] = {"status": "extraction_failed",
                           "checked_on": "2026-10-28", "reason": "PDFParsingError"}
        result, stats = pdf.enrich_queue({"version": 1, "leads": [x]}, [SOURCE],
                                         lambda *_: b"%PDF-mock", fake_extract, "2026-10-28")
        self.assertEqual(stats["successful"], 1)
        self.assertEqual(result["leads"][0]["status"], "needs_human_review")

    def test_repeat_pdf_parsing_error_retries_after_seven_days(self):
        def broken(_):
            raise RuntimeError("PDF parser cannot read mock")
        first, stats = pdf.enrich_queue({"version": 1, "leads": [pending()]}, [SOURCE],
                                        lambda *_: b"%PDF-mock", broken, "2026-10-28")
        self.assertEqual(first["leads"][0]["pdf_review"]["status"], "extraction_failed")
        self.assertEqual(first["leads"][0]["pdf_review"]["retry_after"], "2026-11-04")
        second, stats = pdf.enrich_queue(first, [SOURCE],
                                         lambda *_: (_ for _ in ()).throw(AssertionError),
                                         fake_extract, "2026-10-29")
        self.assertEqual(stats["examined"], 0)
        self.assertEqual(first, second)

    def test_cross_site_redirect_rejected(self):
        handler = pdf.SameSiteRedirectHandler(SOURCE["url"])
        with self.assertRaises(HTTPError):
            handler.redirect_request(Request(URL), None, 302, "redirect", {},
                                     "http://attacker.invalid/fake.pdf")

    def test_empty_pdf_page_requires_ocr(self):
        from pypdf import PdfWriter
        import io
        writer = PdfWriter()
        writer.add_blank_page(width=200, height=200)
        buffer = io.BytesIO()
        writer.write(buffer)
        result = pdf.extract_pdf_evidence(buffer.getvalue())
        self.assertEqual(result["status"], "requires_ocr_or_manual_read")
        self.assertEqual(result["page_count"], 1)
        self.assertEqual(result["evidence"], [])

    def test_untrusted_pdf_body_rejected(self):
        # Offline validation of type/content guard: fake opener.
        from contextlib import contextmanager
        class Response:
            def geturl(self): return URL
            def read(self, n): return b"<!doctype html>no pdf"
            def __enter__(self): return self
            def __exit__(self, *args): return False
        class Opener:
            def open(self, *args, **kwargs): return Response()
        old = pdf.build_opener
        try:
            pdf.build_opener = lambda *args: Opener()
            with self.assertRaises(ValueError):
                pdf.download_official_pdf(URL, SOURCE["url"])
        finally:
            pdf.build_opener = old


if __name__ == "__main__":
    unittest.main()
