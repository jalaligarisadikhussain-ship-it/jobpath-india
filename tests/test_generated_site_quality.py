"""Generated-site regression audit. Run after: python3 scripts/build_final.py."""
from datetime import datetime, timezone
from pathlib import Path
import json
import re
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://jobpath-india.pages.dev"
TODAY = datetime.now(timezone.utc).date().isoformat()

class GeneratedSiteQuality(unittest.TestCase):
    def test_canonical_urls_use_primary_cloudflare_hostname(self):
        pages = json.loads((ROOT / "data/pages.json").read_text(encoding="utf-8"))
        for key, info in pages.items():
            with self.subTest(page=key):
                route = "/" + (info["path"] + "/" if info["path"] else "")
                text = (ROOT / info["path"] / "index.html").read_text(encoding="utf-8")
                canonical = re.search(r'<link rel="canonical" href="([^"]+)">', text)
                social = re.search(r'<meta property="og:url" content="([^"]+)">', text)
                self.assertIsNotNone(canonical)
                self.assertIsNotNone(social)
                self.assertEqual(canonical.group(1), SITE + route)
                self.assertEqual(social.group(1), SITE + route)
                self.assertNotIn("https://jobpath-india.netlify.app/", canonical.group(1))

    def test_static_source_cards_never_claim_expired_deadlines_are_open(self):
        for route in ["", "latest-jobs", "central-government-jobs", "railway-jobs", "banking-jobs"]:
            with self.subTest(route=route):
                text = (ROOT / route / "index.html").read_text(encoding="utf-8")
                cards = re.findall(r'<article class="source-card">.*?</article>', text, re.S)
                for card in cards:
                    match = re.search(r'Application deadline: <time datetime="(\d{4}-\d{2}-\d{2})">', card)
                    if match:
                        self.assertGreaterEqual(match.group(1), TODAY, "Expired job still in public fallback")

    def test_rss_has_only_reviewed_unexpired_recruitment_records(self):
        rss = ET.parse(ROOT / "feed.xml").getroot()
        self.assertEqual(rss.tag, "rss")
        items = rss.find("channel").findall("item")
        self.assertLessEqual(len(items), 80)
        jobs = json.loads((ROOT / "data/jobs.json").read_text(encoding="utf-8"))
        indexed = {str(job["id"]): job for job in jobs}
        seen = set()
        for item in items:
            guid = item.findtext("guid", "")
            self.assertTrue(guid.startswith("jobpath:"))
            jid = guid[len("jobpath:"):]
            self.assertIn(jid, indexed)
            self.assertNotIn(jid, seen)
            seen.add(jid)
            job = indexed[jid]
            self.assertTrue(job.get("verified"))
            self.assertFalse(job.get("isDemo"))
            self.assertEqual(job.get("status"), "open")
            self.assertGreaterEqual(job.get("lastDate"), TODAY)
            self.assertIn("verify official updates", item.findtext("description", ""))
            self.assertTrue(item.findtext("link", "").startswith(SITE + "/job/?id="))
        homepage = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn('rel="alternate" type="application/rss+xml"', homepage)

    def test_sitemap_is_indexable_primary_routes_only(self):
        pages = json.loads((ROOT / "data/pages.json").read_text(encoding="utf-8"))
        urls = {
            item.text for item in ET.parse(ROOT / "sitemap.xml").iter()
            if item.tag.endswith("loc")
        }
        self.assertTrue(urls)
        for url in urls:
            self.assertTrue(url.startswith(SITE + "/"), url)
            route = url[len(SITE):]
            match = [k for k, v in pages.items() if "/" + (v["path"] + "/" if v["path"] else "") == route]
            self.assertEqual(len(match), 1, "Unknown sitemap route: " + url)
            html = (ROOT / pages[match[0]]["path"] / "index.html").read_text(encoding="utf-8")
            self.assertIn('name="robots" content="index,follow"', html)

if __name__ == "__main__":
    unittest.main()
