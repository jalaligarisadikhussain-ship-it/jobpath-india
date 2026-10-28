"""Offline approval-gate tests."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_review_queue import validate_review_queue

SOURCE = {"id": "cwc", "name": "CWC", "url": "https://cwceportal.com/careers"}
BASE = {
    "id": "abc123",
    "source_id": "cwc",
    "source_name": "CWC",
    "source_page": "https://cwceportal.com/careers",
    "title": "Official Recruitment Notification 2026",
    "notice_url": "https://cwceportal.com/Careers/Recruitment2026.pdf",
    "first_seen": "2026-10-28",
    "status": "needs_human_review",
    "review_checklist": {
        "original_notice_checked": False,
        "dates_checked": False,
        "vacancies_checked": False,
        "eligibility_checked": False,
        "application_link_checked": False,
    }
}


class ReviewValidationTests(unittest.TestCase):
    def test_empty_queue_valid(self):
        self.assertEqual(validate_review_queue({"version": 1, "leads": []}, [SOURCE]), [])

    def test_new_unverified_link_valid(self):
        self.assertEqual(validate_review_queue({"version": 1, "leads": [BASE]}, [SOURCE]), [])

    def test_lookalike_official_domain_rejected(self):
        candidate = dict(BASE, notice_url="https://cwceportal.com.attacker.example/Recruitment2026.pdf")
        self.assertTrue(validate_review_queue({"version": 1, "leads": [candidate]}, [SOURCE]))

    def test_unreviewed_candidate_cannot_claim_reviewed(self):
        candidate = dict(BASE, status="reviewed")
        errors = validate_review_queue({"version": 1, "leads": [candidate]}, [SOURCE])
        self.assertTrue(any("every checklist" in e for e in errors))
        self.assertTrue(any("reviewed_by" in e for e in errors))

    def test_reviewed_candidate_requires_human_and_checks(self):
        candidate = dict(BASE, status="reviewed", reviewed_by="editor", reviewed_at="2026-10-28",
                         review_checklist={k: True for k in BASE["review_checklist"]})
        self.assertEqual(validate_review_queue({"version": 1, "leads": [candidate]}, [SOURCE]), [])

    def test_rejection_requires_reason(self):
        candidate = dict(BASE, status="rejected")
        self.assertTrue(validate_review_queue({"version": 1, "leads": [candidate]}, [SOURCE]))

    def test_repeated_links_rejected(self):
        candidate = dict(BASE, id="abc456")
        self.assertTrue(validate_review_queue({"version": 1, "leads": [BASE, candidate]}, [SOURCE]))


if __name__ == "__main__":
    unittest.main()
