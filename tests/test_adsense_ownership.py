"""Ensure AdSense ownership can be checked without serving ads."""
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from adsense_identity import ADSENSE_ACCOUNT_ID, ADSENSE_META_TAG, ADS_TXT_LINE


class AdSenseOwnershipTests(unittest.TestCase):
    def test_verified_public_identity(self):
        self.assertEqual(ADSENSE_ACCOUNT_ID, "ca-pub-8073443569494348")
        self.assertIn('name="google-adsense-account"', ADSENSE_META_TAG)
        self.assertEqual(
            ADS_TXT_LINE,
            "google.com, pub-8073443569494348, DIRECT, f08c47fec0942fa0\n",
        )

    def test_build_prepares_ownership_without_enabling_ads(self):
        subprocess.run([sys.executable, "scripts/build_dist.py"], cwd=ROOT, check=True, capture_output=True)
        homepage = (ROOT / "dist" / "index.html").read_text(encoding="utf-8")
        self.assertIn(ADSENSE_META_TAG, homepage)
        self.assertEqual((ROOT / "dist" / "ads.txt").read_text(encoding="utf-8"), ADS_TXT_LINE)
        self.assertNotIn("pagead2.googlesyndication.com/pagead/js/adsbygoogle.js", homepage)
        self.assertIn("https://jobpath-india.netlify.app/", homepage)


if __name__ == "__main__":
    unittest.main()
