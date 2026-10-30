"""Primary canonical URL is independent of the host serving the static build."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from site_config import search_primary_origin, site_origin, DEFAULT_SITE_URL


class SearchPrimaryTests(unittest.TestCase):
    def test_default_primary_is_verified_cloudflare_pages_site(self):
        self.assertEqual(search_primary_origin({}), DEFAULT_SITE_URL)
        self.assertEqual(DEFAULT_SITE_URL, "https://jobpath-india.pages.dev")

    def test_render_copy_can_use_separate_origin(self):
        self.assertEqual(
            site_origin({"RENDER": "true", "RENDER_EXTERNAL_URL": "https://jobpath-india.onrender.com"}),
            "https://jobpath-india.onrender.com",
        )
        self.assertEqual(search_primary_origin({"RENDER": "true"}), DEFAULT_SITE_URL)

    def test_primary_override_is_available_for_future_migrations(self):
        self.assertEqual(
            search_primary_origin({"JOBPATH_PRIMARY_SEARCH_URL": "https://jobpath-india.onrender.com"}),
            "https://jobpath-india.onrender.com",
        )

    def test_invalid_primary_origin_rejected(self):
        with self.assertRaises(ValueError):
            search_primary_origin({"JOBPATH_PRIMARY_SEARCH_URL": "https://example.com/invalid"})


if __name__ == "__main__":
    unittest.main()
