"""Offline tests of approval-triggered job publishing. Fake job never reaches website."""
import copy
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import publish_approved as pub

TODAY = date(2026, 10, 28)
SOURCE = {"id": "cwc", "name": "Central Warehousing Corporation — Careers",
          "url": "https://cwceportal.com/careers"}


def candidate():
    return {
        "id": "TEST-PUBLISH-2026-001",
        "title": "Test Technical Officer",
        "organization": "Central Warehousing Corporation",
        "type": "Central", "state": "All India",
        "qualification": "B.Tech / Engineering",
        "department": "Technical", "category": "PSU",
        "minAge": 18, "maxAge": 30, "vacancies": 12,
        "payScale": "Refer to official notice",
        "startDate": "2026-10-15", "lastDate": "2026-11-15",
        "publishedDate": "2026-10-10", "fees": "Read official notice",
        "selectionProcess": "See notification",
        "notificationUrl": "https://cwceportal.com/Careers/Guidelines/2026-notice.pdf",
        "applicationUrl": "https://cwceportal.com/Apply/2026",
        "sourceOrganization": "CWC official recruitment notification",
        "lastVerifiedDate": "2026-10-28",
        "verified": True, "isDemo": False, "status": "open",
        "description": "Unit test example. This fixture is never published."
    }


def lead():
    job = candidate()
    return {
        "id": "test-notice-001", "source_id": "cwc",
        "source_name": SOURCE["name"], "source_page": SOURCE["url"],
        "title": "Recruitment notice for Test Technical Officer",
        "notice_url": job["notificationUrl"],
        "first_seen": "2026-10-20", "status": "reviewed",
        "reviewed_by": "Test Editor", "reviewed_at": "2026-10-28",
        "auto_publish_approved": True,
        "review_checklist": {
            "original_notice_checked": True, "dates_checked": True,
            "vacancies_checked": True, "eligibility_checked": True,
            "application_link_checked": True
        }, "approved_job": job,
    }


def run(leads, jobs=None, ledger=None):
    return pub.prepare_publication({"version": 1, "leads": leads},
                                   jobs or [], [SOURCE], ledger or {"version": 1, "published": []}, TODAY)


class AutoPublishTests(unittest.TestCase):
    def test_no_approved_leads_does_not_publish(self):
        jobs, ledger, added, issues = run([])
        self.assertEqual((jobs, added, issues), ([], [], []))

    def test_detected_link_not_auto_published(self):
        x = lead()
        x["status"] = "needs_human_review"
        x.pop("reviewed_at")
        x.pop("reviewed_by")
        result = run([x])
        self.assertEqual(result[2], [])
        self.assertEqual(result[0], [])

    def test_reviewed_but_not_explicitly_approved_stays_private(self):
        x = lead()
        x["auto_publish_approved"] = False
        jobs, ledger, added, errors = run([x])
        self.assertEqual((jobs, added, errors), ([], [], []))

    def test_unverified_pdf_cannot_trigger_auto_publication(self):
        x = lead()
        x["review_checklist"]["vacancies_checked"] = False
        self.assertTrue(run([x])[3])

    def test_human_approved_notice_publishes_automatically(self):
        jobs, ledger, added, issues = run([lead()])
        self.assertFalse(issues)
        self.assertEqual(added, ["TEST-PUBLISH-2026-001"])
        self.assertTrue(jobs[0]["verified"])
        self.assertEqual(ledger["published"][0]["source_lead_id"], "test-notice-001")
        self.assertNotIn("reviewed_by", jobs[0])

    def test_repeated_run_idempotent_no_duplicate_job(self):
        jobs, ledger, added, issues = run([lead()])
        jobs2, ledger2, added2, issues2 = run([lead()], jobs=jobs, ledger=ledger)
        self.assertEqual((jobs2, ledger2), (jobs, ledger))
        self.assertFalse(added2)
        self.assertFalse(issues2)

    def test_off_site_notice_rejected(self):
        x = lead()
        x["notice_url"] = "https://cwceportal.com.attacker.invalid/notice.pdf"
        x["approved_job"]["notificationUrl"] = x["notice_url"]
        self.assertTrue(run([x])[3])

    def test_missing_human_approval_rejected(self):
        x = lead()
        x.pop("approved_job")
        self.assertTrue(run([x])[3])

    def test_stale_review_is_not_auto_published(self):
        x = lead()
        x["reviewed_at"] = "2026-10-01"
        x["approved_job"]["lastVerifiedDate"] = "2026-10-01"
        self.assertTrue(run([x])[3])

    def test_future_review_date_rejected(self):
        x = lead()
        x["reviewed_at"] = "2026-11-01"
        x["approved_job"]["lastVerifiedDate"] = "2026-11-01"
        self.assertTrue(run([x])[3])

    def test_expired_vacancy_rejected(self):
        x = lead()
        x["approved_job"]["lastDate"] = "2026-10-27"
        self.assertTrue(run([x])[3])

    def test_status_must_reflect_open_window(self):
        x = lead()
        x["approved_job"]["status"] = "upcoming"
        self.assertTrue(run([x])[3])

    def test_missing_vacancy_count_rejected(self):
        x = lead()
        x["approved_job"]["vacancies"] = None
        self.assertTrue(run([x])[3])

    def test_off_site_application_host_rejected(self):
        x = lead()
        x["approved_job"]["applicationUrl"] = "https://fakejobscareers.invalid/apply"
        self.assertTrue(run([x])[3])

    def test_authorized_off_site_application_requires_extra_human_check(self):
        x = lead()
        x["approved_job"]["applicationUrl"] = "https://ibpsreg.ibps.in/test/"
        self.assertTrue(run([x])[3])
        x["application_host_independently_verified"] = True
        self.assertFalse(run([x])[3])

    def test_reject_authorized_off_site_with_subdomain_lookalike(self):
        x = lead()
        x["approved_job"]["applicationUrl"] = "https://ibpsreg.ibps.in.attack.invalid/test"
        x["application_host_independently_verified"] = True
        self.assertTrue(run([x])[3])

    def test_tampered_job_notice_url_rejected(self):
        x = lead()
        x["approved_job"]["notificationUrl"] = "https://cwceportal.com/another.pdf"
        self.assertTrue(run([x])[3])

    def test_rejected_or_unreviewed_leads_never_publish(self):
        x = lead()
        x["status"] = "rejected"
        x["rejection_reason"] = "Not an open job"
        self.assertEqual(run([x])[2], [])

    def test_existing_job_with_same_id_is_not_overwritten(self):
        x = lead()
        existing = copy.deepcopy(x["approved_job"])
        existing["description"] = "Prior editor-reviewed description"
        jobs, ledger, added, issues = run([x], jobs=[existing])
        self.assertFalse(issues)
        self.assertFalse(added)
        self.assertEqual(jobs[0]["description"], existing["description"])

    def test_existing_job_with_same_id_different_notice_blocked(self):
        x = lead()
        existing = copy.deepcopy(x["approved_job"])
        existing["notificationUrl"] = "https://cwceportal.com/another-notice.pdf"
        self.assertTrue(run([x], jobs=[existing])[3])

    def test_multiple_candidates_atomic_if_one_is_invalid(self):
        good = lead()
        bad = lead()
        bad["id"] = "different-lead"
        bad["approved_job"]["id"] = "OTHER-JOB-001"
        bad["approved_job"]["vacancies"] = 0
        jobs, ledger, added, issues = run([good, bad])
        self.assertEqual(jobs, [])
        self.assertEqual(added, [])
        self.assertTrue(issues)

    def test_unknown_source_must_not_publish(self):
        x = lead()
        x["source_id"] = "upsc"
        self.assertTrue(run([x])[3])


if __name__ == "__main__":
    unittest.main()
