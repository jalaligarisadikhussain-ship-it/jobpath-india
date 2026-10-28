"""Offline tests for safe IST-date transitions; no government-site requests."""
import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from sync_job_status import sync_status


def base(**changes):
    value = {
        "id": "TEST-CWC-JOB", "verified": True, "isDemo": False,
        "status": "open", "startDate": "2026-10-17", "lastDate": "2026-10-28",
        "lastVerifiedDate": "2026-10-20", "title": "Unit test role"
    }
    value.update(changes)
    return value


class StatusSyncTests(unittest.TestCase):
    def test_deadline_today_is_still_open(self):
        result, changes = sync_status([base()], date(2026, 10, 28))
        self.assertEqual(result[0]["status"], "open")
        self.assertFalse(changes)

    def test_close_day_after_deadline(self):
        result, changes = sync_status([base()], date(2026, 10, 29))
        self.assertEqual(result[0]["status"], "closed")
        self.assertEqual(changes[0]["from"], "open")
        self.assertEqual(changes[0]["to"], "closed")

    def test_never_extend_deadline_or_reverify_implicitly(self):
        result, _ = sync_status([base()], date(2026, 10, 29))
        self.assertEqual(result[0]["lastDate"], "2026-10-28")
        self.assertEqual(result[0]["lastVerifiedDate"], "2026-10-20")

    def test_upcoming_to_open_only_after_start_date(self):
        x = base(startDate="2026-11-01", lastDate="2026-11-30", status="upcoming")
        result, changes = sync_status([x], date(2026, 11, 1))
        self.assertEqual(result[0]["status"], "open")
        self.assertEqual(changes[0]["from"], "upcoming")

    def test_future_open_becomes_upcoming(self):
        x = base(startDate="2026-11-01", lastDate="2026-11-30")
        result, changes = sync_status([x], date(2026, 10, 28))
        self.assertEqual(result[0]["status"], "upcoming")
        self.assertEqual(len(changes), 1)

    def test_deliberately_closed_stays_closed(self):
        result, changes = sync_status([base(status="closed", lastDate="2026-12-30")], date(2026, 10, 28))
        self.assertEqual(result[0]["status"], "closed")
        self.assertFalse(changes)

    def test_unverified_and_demo_records_unchanged(self):
        items = [base(verified=False), base(isDemo=True), base(status="unverified", verified=False)]
        result, changes = sync_status(items, date(2026, 11, 30))
        self.assertEqual(result, items)
        self.assertFalse(changes)

    def test_invalid_record_date_skipped(self):
        items = [base(lastDate="2026-11-31"), base(startDate="not-a-date")]
        result, changes = sync_status(items, date(2026, 12, 1))
        self.assertEqual(result, items)
        self.assertFalse(changes)

    def test_no_duplicate_or_missing_jobs(self):
        items = [base(id="A"), base(id="B", status="closed"),
                 base(id="C", isDemo=True)]
        result, changes = sync_status(items, date(2026, 11, 1))
        self.assertEqual([x["id"] for x in result], ["A", "B", "C"])
        self.assertEqual(len(changes), 1)

    def test_idempotent_after_first_transition(self):
        result, changes = sync_status([base()], date(2026, 10, 29))
        result2, changes2 = sync_status(result, date(2026, 10, 29))
        self.assertEqual(result2, result)
        self.assertFalse(changes2)
        self.assertEqual(len(changes), 1)


if __name__ == "__main__":
    unittest.main()
