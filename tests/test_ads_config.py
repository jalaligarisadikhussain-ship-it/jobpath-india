"""Advertising stays off without exact external AdSense IDs."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from validate_ads_config import load_and_validate,validate

class AdvertisingConfigurationTests(unittest.TestCase):
    def test_repository_config_is_structurally_valid(self):
        self.assertEqual(validate(load_and_validate()), [])

    def test_off_does_not_allow_accidental_tracking_identifiers(self):
        self.assertFalse(validate({"enabled":False,"provider":"none","publisherId":"","slots":{"content":""}}))
        self.assertTrue(validate({"enabled":False,"provider":"none","publisherId":"ca-pub-1234567890123456","slots":{"content":""}}))

    def test_real_adsense_identifiers_required_to_enable(self):
        self.assertEqual(validate({"enabled":True,"provider":"adsense","publisherId":"ca-pub-1234567890123456","slots":{"content":"1234567890"}}),[])
        self.assertTrue(validate({"enabled":True,"provider":"adsense","publisherId":"ca-pub-fake","slots":{"content":"1234567890"}}))
        self.assertTrue(validate({"enabled":True,"provider":"adsense","publisherId":"ca-pub-1234567890123456","slots":{"content":""}}))

    def test_script_injection_is_rejected(self):
        self.assertTrue(validate({"enabled":True,"provider":"adsense","publisherId":"ca-pub-123</script>","slots":{"content":"1234567890"}}))
        self.assertTrue(validate({"enabled":True,"provider":"adsense","publisherId":"ca-pub-1234567890123456","slots":{"content":"123\" onclick=alert(1)"}}))
if __name__ == "__main__":
    unittest.main()
