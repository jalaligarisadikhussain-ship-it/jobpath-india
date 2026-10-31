"""Exercise complete static releases for existing and additional hosting origins."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from site_config import DEFAULT_SITE_URL, LEGACY_NETLIFY_URL, site_origin
from adsense_identity import ADSENSE_META_TAG, ADS_TXT_LINE


class HostingBuildTests(unittest.TestCase):
    def test_cloudflare_is_default_and_render_metadata_is_scoped(self):
        self.assertEqual(site_origin({}), DEFAULT_SITE_URL)
        self.assertEqual(site_origin({"RENDER_EXTERNAL_URL": "https://other.invalid"}), DEFAULT_SITE_URL)

    def test_explicit_verified_domain_can_override_render_origin(self):
        self.assertEqual(site_origin({"JOBPATH_SITE_URL": "https://jobs.example/", "RENDER": "true",
                                      "RENDER_EXTERNAL_URL": "https://render-test.invalid"}),
                         "https://jobs.example")

    def test_unsafe_or_non_origin_values_fail_before_generating_pages(self):
        for value in ["http://jobs.example", "//jobs.example", "https://user:pass@jobs.example",
                      "https://jobs.example/path", "https://jobs.example?x=1", "https://jobs.example#",
                      "https://jobs.example:443", "https://jobs.example\n", "https://jobs.example/<script>",
                      "https://jobs.example\\other", "https://localhost", "https://-jobs.example"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                site_origin({"JOBPATH_SITE_URL": value})

    def check_release(self, env_settings, origin):
        with tempfile.TemporaryDirectory(prefix="jobpath-hosting-") as tmp:
            work = Path(tmp)
            for folder in ("scripts", "data", "assets"):
                shutil.copytree(ROOT / folder, work / folder, ignore=shutil.ignore_patterns("__pycache__"))
            shutil.copyfile(ROOT / "googlefcd24aba957dc07b.html", work / "googlefcd24aba957dc07b.html")
            env = dict(os.environ)
            for key in ("JOBPATH_SITE_URL", "JOBPATH_PRIMARY_SEARCH_URL", "RENDER", "RENDER_EXTERNAL_URL"):
                env.pop(key, None)
            env.update(env_settings)
            subprocess.run([sys.executable, "scripts/build_dist.py"], cwd=work, env=env,
                           check=True, capture_output=True, text=True)
            dist = work / "dist"
            pages = json.loads((ROOT / "data/pages.json").read_text())
            for page in pages.values():
                route = "/" + (page["path"] + "/" if page["path"] else "")
                text = (dist / page["path"] / "index.html").read_text()
                self.assertIn(f'<link rel="canonical" href="{DEFAULT_SITE_URL}{route}">', text)
                self.assertIn(f'<meta property="og:url" content="{DEFAULT_SITE_URL}{route}">', text)
                graph = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', text)[1])
                self.assertEqual(graph["@graph"][0]["url"], DEFAULT_SITE_URL + "/")
                self.assertEqual(graph["@graph"][1]["url"], DEFAULT_SITE_URL + route)
                self.assertIn(ADSENSE_META_TAG, text)
                self.assertNotRegex(text, r'<script[^>]+src="https://(?:bauval\.org|pagead2\.googlesyndication\.com)')
            sitemap = ET.parse(dist / "sitemap.xml")
            locations = [node.text for node in sitemap.findall(".//{*}loc")]
            self.assertEqual(len(locations), 25 if origin == DEFAULT_SITE_URL else 0)
            self.assertTrue(all(url.startswith(DEFAULT_SITE_URL + "/") for url in locations))
            self.assertNotIn(origin + "/auto-recruitment-notices/", locations)
            self.assertIn(f"Sitemap: {origin}/sitemap.xml\n", (dist / "robots.txt").read_text())
            # All three full-format banner tags were supplied by the owner.
            for name, key in (
                ('mobile','22d5d7312497a4575a8261d0d18522ea'),
                ('desktop','5b1925f1b2ab32ef7b6d207bde9e0fa1'),
                ('rectangle','58623b07e46a924f55b4d5d4895086c0'),
            ):
                banner_page=dist/'ad-units'/(name+'.html')
                self.assertTrue(banner_page.is_file())
                self.assertIn('https://bauval.org/22/'+key,banner_page.read_text())
                self.assertIn('var atOptions',banner_page.read_text())
                # Regression check: the generated probe previously used // inside a
                # one-line JS string and accidentally commented out its closing
                # braces and MutationObserver setup. Compile the emitted JS.
                html=banner_page.read_text()
                inline=re.findall(r'<script>(.*?)</script>',html,re.DOTALL)
                self.assertEqual(len(inline),2)
                self.assertIn('jobpath-banner-fill',inline[-1])
                self.assertNotIn('// An iframe existing',inline[-1])
                node=shutil.which('node')
                self.assertIsNotNone(node,'Node.js needed to syntax-check ad probes')
                for snippet in inline:
                    result=subprocess.run([node,'--check','-'],input=snippet,
                                          text=True,capture_output=True,check=False)
                    self.assertEqual(result.returncode,0,result.stderr)
            for name in ("jobs.json", "auto-notices.json", "ads-config.json"):
                self.assertEqual((dist / "data" / name).read_bytes(), (ROOT / "data" / name).read_bytes())
            self.assertFalse(json.loads((dist / "data/ads-config.json").read_text())["enabled"])
            for private in ("scripts", "reports", "tests", ".github", "RENDER_DEPLOYMENT_SETUP.md"):
                self.assertFalse((dist / private).exists())
            self.assertEqual((dist / "ads.txt").read_text(), ADS_TXT_LINE)

    def test_cloudflare_primary_has_indexable_sitemap_and_self_canonical(self):
        self.check_release({}, DEFAULT_SITE_URL)

    def test_legacy_netlify_origin_is_preserved_as_duplicate_with_cloudflare_canonical(self):
        self.check_release({"JOBPATH_SITE_URL": LEGACY_NETLIFY_URL}, LEGACY_NETLIFY_URL)

    def test_complete_render_release_uses_cloudflare_primary_canonical_without_activating_ads(self):
        self.check_release({"RENDER": "true", "RENDER_EXTERNAL_URL": "https://jobpath-render-test.invalid"},
                           "https://jobpath-render-test.invalid")


if __name__ == "__main__":
    unittest.main()
