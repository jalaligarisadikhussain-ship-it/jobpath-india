"""Offline tests: no network requests and no public job publishing."""
import importlib.util
import unittest
from pathlib import Path
from urllib.error import HTTPError

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("review", root / "scripts" / "discover_notice_leads.py")
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


class ReviewLeadTests(unittest.TestCase):
    def setUp(self):
        self.source = {"id": "cwc", "name": "Central Warehousing Corporation",
                       "url": "https://cwceportal.com/careers"}
        self.pdf = "https://cwceportal.com/Careers/Guidelines/45/Advertisement2026.pdf"
        self.markup = ('<a href="/Careers/Guidelines/45/Advertisement2026.pdf">'
                       'Advertisement for Recruitment 2026</a>')
        self.today = "2026-10-28"

    def test_official_pdf_is_unverified_lead_only(self):
        leads = review.discover_from_html(self.source, self.markup, set(), self.today)
        self.assertEqual(len(leads), 1)
        self.assertEqual(leads[0]["notice_url"], self.pdf)
        self.assertEqual(leads[0]["status"], "needs_human_review")
        self.assertFalse(any(leads[0]["review_checklist"].values()))
        self.assertNotIn("vacancies", leads[0])
        self.assertNotIn("lastDate", leads[0])

    def test_outside_domain_rejected(self):
        bad = '<a href="https://cwceportal.com.evil.example/recruitment2026.pdf">Notice</a>'
        self.assertEqual(review.discover_from_html(self.source, bad, set(), self.today), [])

    def test_third_party_application_link_rejected(self):
        bad = '<a href="https://ibpsreg.ibps.in/abc2026.pdf">Recruitment 2026</a>'
        self.assertEqual(review.discover_from_html(self.source, bad, set(), self.today), [])

    def test_script_and_insecure_link_rejected(self):
        markup = ('<a href="javascript:alert(1)">Recruitment 2026</a>'
                  '<a href="http://cwceportal.com/recruitment/2026.pdf">Recruitment 2026</a>')
        self.assertEqual(review.discover_from_html(self.source, markup, set(), self.today), [])

    def test_generic_navigation_not_treated_as_notice(self):
        markup = '<a href="/careers">Careers</a><a href="/recruitment">Recruitment</a>'
        self.assertEqual(review.discover_from_html(self.source, markup, set(), self.today), [])

    def test_duplicate_notice_skipped(self):
        leads = review.discover_from_html(self.source, self.markup + self.markup, set(), self.today)
        self.assertEqual(len(leads), 1)
        second = review.discover_from_html(self.source, self.markup, {self.pdf}, self.today)
        self.assertEqual(second, [])

    def test_published_notice_is_not_queued(self):
        published = [{"notificationUrl": self.pdf, "verified": True}]
        queue, checks = review.update_queue([self.source], {"version": 1, "leads": []},
                                             published, lambda url: self.markup, self.today)
        self.assertEqual(queue["leads"], [])
        self.assertEqual(len(checks), 1)

    def test_existing_queue_stable_on_next_run(self):
        first, _ = review.update_queue([self.source], {"version": 1, "leads": []}, [],
                                        lambda url: self.markup, self.today)
        second, _ = review.update_queue([self.source], first, [],
                                         lambda url: self.markup, "2026-10-29")
        self.assertEqual(first, second)

    def test_inaccessible_official_site_does_not_remove_leads(self):
        first, _ = review.update_queue([self.source], {"version": 1, "leads": []}, [],
                                        lambda url: self.markup, self.today)
        def reject(url):
            raise HTTPError(url, 403, "Forbidden", None, None)
        second, checks = review.update_queue([self.source], first, [], reject, "2026-10-29")
        self.assertEqual(first, second)
        self.assertIn("could not inspect", checks[0][1])

    def test_unlisted_sources_are_not_fetched(self):
        bogus = {"id": "unknown", "name": "Unknown", "url": "https://example.com/jobs"}
        def forbidden(url):
            raise AssertionError("unknown source must not be fetched")
        result, checks = review.update_queue([bogus], {"version": 1, "leads": []},
                                              [], forbidden, self.today)
        self.assertEqual(result["leads"], [])
        self.assertEqual(checks, [])

    def test_review_report_does_not_claim_automatic_publication(self):
        queue, _ = review.update_queue([self.source], {"version": 1, "leads": []}, [],
                                       lambda url: self.markup, self.today)
        output = review.report_md(queue)
        self.assertIn("Needs review", output)
        self.assertIn("NOT published jobs", output)
        self.assertIn("does not edit the public jobs database", output)

    def test_path_with_misleading_document_name_rejected(self):
        markup = '<a href="/files/expense2026.pdf">Finance Department</a>'
        self.assertEqual(review.discover_from_html(self.source, markup, set(), self.today), [])


if __name__ == "__main__":
    unittest.main()
