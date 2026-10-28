"""All tests offline: automatic source-notice publishing never invents live vacancies."""
import copy
import sys
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import publish_detected_notices as auto

TODAY = date(2026, 10, 28)
SOURCE = {"id": "cwc", "name": "Central Warehousing Corporation",
          "url": "https://cwceportal.com/careers"}


def lead(**changes):
    record = {
        "id": "testnotice1",
        "source_id": "cwc",
        "source_name": SOURCE["name"],
        "source_page": SOURCE["url"],
        "title": "Advertisement for Recruitment 2026",
        "notice_url": "https://cwceportal.com/Careers/Recruitment2026.pdf",
        "first_seen": TODAY.isoformat(),
        "status": "needs_human_review",
        "review_checklist": {
            "original_notice_checked": False, "dates_checked": False,
            "vacancies_checked": False, "eligibility_checked": False,
            "application_link_checked": False,
        },
    }
    record.update(changes)
    return record


def feed(records, jobs=None):
    return auto.build_public_feed({"version": 1, "leads": records}, [SOURCE], jobs or [], TODAY)


class AutomaticNoticePublishingTests(unittest.TestCase):
    def test_unreviewed_notice_appears_publicly_as_unverified(self):
        published = feed([lead()])["notices"]
        self.assertEqual(len(published), 1)
        self.assertEqual(published[0]["verificationStatus"], "automatically_detected_unverified")
        self.assertEqual(published[0]["applicationStatus"], "unknown")
        for field in ("verified", "vacancies", "lastDate", "applicationUrl", "fees"):
            self.assertNotIn(field, published[0])

    def test_duplicate_source_link_excluded_when_verified_job_already_published(self):
        jobs = [{"notificationUrl": lead()["notice_url"], "verified": True, "isDemo": False}]
        self.assertEqual(feed([lead()], jobs)["notices"], [])

    def test_rejected_notices_never_published(self):
        rejected = lead(status="rejected", rejection_reason="Not recruitment")
        self.assertEqual(feed([rejected])["notices"], [])

    def test_expired_detection_is_removed(self):
        stale = lead(first_seen=(TODAY - timedelta(days=46)).isoformat())
        self.assertEqual(feed([stale])["notices"], [])

    def test_future_detected_date_rejected(self):
        future = lead(first_seen=(TODAY + timedelta(days=1)).isoformat())
        self.assertEqual(feed([future])["notices"], [])

    def test_fake_external_domain_blocked(self):
        bogus = lead(notice_url="https://cwceportal.com.attacker.example/Recruitment2026.pdf")
        with self.assertRaises(ValueError):
            feed([bogus])

    def test_html_snippets_remain_data_not_markup(self):
        xss = lead(title="<img src=x onerror=alert(1)> Recruitment 2026")
        published = feed([xss])["notices"]
        self.assertEqual(len(published), 1)
        self.assertNotIn("verified", published[0])
        self.assertIn("<img", published[0]["title"])
        # Frontend and SSR must escape title, never insert it as raw HTML.

    def test_results_do_not_look_like_recruitment(self):
        results = lead(title="Recruitment result and selected candidate merit list 2026")
        self.assertEqual(feed([results])["notices"], [])

    def test_source_only_in_allowlist(self):
        other = copy.deepcopy(SOURCE)
        other["id"] = "upsc"
        record = lead(source_id="upsc", source_page=SOURCE["url"])
        # Source provenance succeeds but auto public allowlist must still block.
        self.assertEqual(auto.build_public_feed({"version": 1, "leads": [record]},
                                                [other], [], TODAY)["notices"], [])

    def test_missing_vacancy_data_does_not_stop_notice_publication(self):
        self.assertEqual(len(feed([lead()])["notices"]), 1)

    def test_nothing_detected_gives_empty_feed(self):
        self.assertEqual(feed([]), {"version": 1, "notices": []})


if __name__ == "__main__":
    unittest.main()
