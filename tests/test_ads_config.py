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
        config["adsterra"]["gamblingExclusionConfirmed"] = True  # simulated network confirmation for activation tests only
        return config

    def test_approved_native_code_and_consent_are_required(self):
        config=self.native_config()
        self.assertEqual(validate(config),[])
        for key,value in [("siteStatus","pending"),("adUnitStatus","inactive")]:
            bad=copy.deepcopy(config);bad["adsterra"][key]=value
            self.assertTrue(validate(bad))
        config["consent"]["required"]=False
        self.assertTrue(validate(config))

    def test_gambling_exclusion_is_mandatory_before_adsterra_activation(self):
        config=self.native_config()
        self.assertEqual(validate(config), [])
        for unconfirmed in (False, None, "true"):
            config["adsterra"]["gamblingExclusionConfirmed"]=unconfirmed
            self.assertTrue(any("gambling" in error for error in validate(config)))
        # Real production config stays disabled because exclusion is not confirmed.
        live=load_and_validate()
        self.assertFalse(live["enabled"])
        self.assertIs(live["adsterra"]["gamblingExclusionConfirmed"], False)

    def test_adsterra_script_cannot_be_replaced_or_injected(self):
        for value in ["https://example.com/invoke.js","javascript:alert(1)",
                      "https://bauval.org/21/59088646af2816821f7d8b37df198113?track=1"]:
            bad=self.native_config();bad["adsterra"]["scriptUrl"]=value
            self.assertTrue(validate(bad))
        bad=self.native_config();bad["adsterra"]["websiteId"]="6156497"
        self.assertTrue(validate(bad))

    def test_malformed_native_config_fails_closed(self):
        for value in [None,[],"<script>"]:
            bad=self.native_config();bad["adsterra"]=value
            self.assertTrue(validate(bad))

    def test_cloudflare_native_unit_is_distinct_and_validated(self):
        cfg=copy.deepcopy(load_and_validate())
        self.assertFalse(cfg["enabled"])  # other hosts remain OFF
        self.assertTrue(cfg["cloudflareAdsterra"]["enabled"])
        self.assertEqual(cfg["cloudflareAdsterra"]["siteStatus"], "unverified")
        self.assertTrue(cfg["cloudflareAdsterra"]["allowUnfilteredCategories"])
        self.assertTrue(cfg["cloudflareAdsterra"]["userAuthorizedTrial"])
        self.assertTrue(cfg["cloudflareAdsterra"]["automaticDisplay"])
        self.assertFalse(cfg["cloudflareAdsterra"]["datingExclusionConfirmed"])
        self.assertFalse(cfg["cloudflareAdsterra"]["gamblingExclusionConfirmed"])
        self.assertFalse(cfg["cloudflareAdsterra"]["adultAds"])
        self.assertEqual(validate(cfg), [])
        for key,value in [("websiteHost","example.com"),("scriptUrl","https://example.com/x"),
                          ("key","malicious"),("adultAds",True),("adUnitStatus","inactive"),
                          ("allowUnfilteredCategories","yes"),("datingExclusionConfirmed","not-bool")]:
            bad=copy.deepcopy(cfg)
            bad["cloudflareAdsterra"][key]=value
            self.assertTrue(validate(bad), key)

    def test_unfiltered_category_trial_is_explicit_and_host_bound(self):
        cfg=copy.deepcopy(load_and_validate())
        self.assertTrue(cfg["cloudflareAdsterra"]["enabled"])
        self.assertFalse(cfg["enabled"])  # Netlify/Render stay disabled
        self.assertEqual(validate(cfg),[])
        for patch in ({"userAuthorizedTrial":False},{"allowUnfilteredCategories":False},
                      {"siteStatus":"pending"},{"adUnitStatus":"inactive"}):
            bad=copy.deepcopy(cfg)
            bad["cloudflareAdsterra"].update(patch)
            self.assertTrue(validate(bad),patch)
        restricted=copy.deepcopy(cfg)
        restricted["cloudflareAdsterra"].update(userAuthorizedTrial=False,allowUnfilteredCategories=False,
             siteStatus="approved",gamblingExclusionConfirmed=True,datingExclusionConfirmed=True)
        self.assertEqual(validate(restricted),[])

    def test_three_site_specific_banner_codes_are_validated(self):
        config=copy.deepcopy(load_and_validate())
        self.assertEqual(validate(config),[])
        self.assertEqual(set(config['cloudflareBanners']['units']), {'mobile','desktop','rectangle'})
        self.assertFalse(config['cloudflareBanners']['enabled'])
        self.assertFalse(config['cloudflareBanners']['deliveryVerified'])
        self.assertTrue(config['cloudflareBanners']['units']['mobile']['sourceVerified'])
        self.assertTrue(config['cloudflareBanners']['units']['desktop']['sourceVerified'])
        self.assertTrue(config['cloudflareBanners']['units']['rectangle']['sourceVerified'])
        for bad_flag in ('yes', None, 1):
            bad=copy.deepcopy(config)
            bad['cloudflareBanners']['deliveryVerified']=bad_flag
            self.assertTrue(validate(bad),bad_flag)
        for name in ('mobile','desktop','rectangle'):
            bad_status=copy.deepcopy(config)
            bad_status['cloudflareBanners']['units'][name]['sourceVerified']='yes'
            self.assertTrue(validate(bad_status),name)
            bad=copy.deepcopy(config)
            bad['cloudflareBanners']['units'][name]['scriptUrl']='https://example.com/malicious.js'
            self.assertTrue(validate(bad),name)

    def test_native_provider_cannot_mix_google_ids(self):
        bad=self.native_config();bad["publisherId"]="ca-pub-8073443569494348"
        self.assertTrue(validate(bad))
if __name__ == "__main__":
    unittest.main()
