"""Advertising activation requires exact provider information and safeguards."""
import copy
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

    def native_config(self):
        config=copy.deepcopy(load_and_validate())
        config.update(enabled=True,provider="adsterra")
        config["adsterra"]["siteStatus"]="approved"
        return config

    def test_approved_native_code_and_consent_are_required(self):
        config=self.native_config()
        self.assertEqual(validate(config),[])
        for key,value in [("siteStatus","pending"),("adUnitStatus","inactive")]:
            bad=copy.deepcopy(config);bad["adsterra"][key]=value
            self.assertTrue(validate(bad))
        config["consent"]["required"]=False
        self.assertTrue(validate(config))

    def test_adsterra_script_cannot_be_replaced_or_injected(self):
        for value in ["https://example.com/invoke.js","javascript:alert(1)",
                      "https://bauval.org/21/84de856c9d01a37c08d4912fbf3df530?track=1"]:
            bad=self.native_config();bad["adsterra"]["scriptUrl"]=value
            self.assertTrue(validate(bad))
        bad=self.native_config();bad["adsterra"]["websiteHost"]="example.com"
        self.assertTrue(validate(bad))

    def test_malformed_native_config_fails_closed(self):
        for value in [None,[],"<script>"]:
            bad=self.native_config();bad["adsterra"]=value
            self.assertTrue(validate(bad))

    def test_native_provider_cannot_mix_google_ids(self):
        bad=self.native_config();bad["publisherId"]="ca-pub-8073443569494348"
        self.assertTrue(validate(bad))
if __name__ == "__main__":
    unittest.main()
