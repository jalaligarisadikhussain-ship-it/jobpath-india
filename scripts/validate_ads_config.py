#!/usr/bin/env python3
"""Validate public ad configuration; approved code is separate from activation."""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "data" / "ads-config.json"
PUBLISHER_RE = re.compile(r"ca-pub-[0-9]{16}\Z")
SLOT_RE = re.compile(r"[0-9]{8,12}\Z")
# Exact public tag observed in JOBPATH INDIA's authenticated Adsterra account.
# A new provider host or ad unit requires an explicit code review, not a URL edit.
ADSTERRA_KEY = "59088646af2816821f7d8b37df198113"
ADSTERRA_SCRIPT = f"https://bauval.org/21/{ADSTERRA_KEY}"


def validate_adsterra(ad):
    if not isinstance(ad, dict):
        return ["adsterra must be an object"]
    expected = {"websiteId": "6159057", "adUnitId": "31978670", "format": "native",
                "key": ADSTERRA_KEY, "scriptUrl": ADSTERRA_SCRIPT,
                "containerId": f"container-{ADSTERRA_KEY}", "adultAds": False}
    errors = [f"Adsterra {key} must match the verified JOBPATH INDIA tag"
              for key, value in expected.items() if ad.get(key) != value]
    if ad.get("adultAds") is not False:
        errors.append("Adult ads must remain disabled")
    if ad.get("siteStatus") not in ("approved", "pending", "rejected"):
        errors.append("Unknown Adsterra site status")
    if ad.get("adUnitStatus") not in ("active", "pending", "inactive"):
        errors.append("Unknown Adsterra ad unit status")
    return errors


# A separate Cloudflare-specific unit is validated without altering Netlify's unit.
CF_ADSTERRA_KEY = "84de856c9d01a37c08d4912fbf3df530"
CF_ADSTERRA_SCRIPT = f"https://bauval.org/21/{CF_ADSTERRA_KEY}"

def validate_cloudflare_adsterra(ad):
    if not isinstance(ad, dict):
        return ["cloudflareAdsterra must be an object"]
    expected = {
        "websiteHost": "jobpath-india.pages.dev",
        "format": "native",
        "key": CF_ADSTERRA_KEY,
        "scriptUrl": CF_ADSTERRA_SCRIPT,
        "containerId": f"container-{CF_ADSTERRA_KEY}",
        "adUnitStatus": "active",
        "adultAds": False,
    }
    errors = [f"Cloudflare Adsterra {key} must match the website-specific tag"
              for key,value in expected.items() if ad.get(key) != value]
    if type(ad.get("enabled")) is not bool:
        errors.append("Cloudflare Adsterra enabled must be a boolean")
    if ad.get("siteStatus") not in ("unverified", "pending", "approved", "rejected"):
        errors.append("Unknown Cloudflare Adsterra website status")
    if "allowUnfilteredCategories" in ad and type(ad["allowUnfilteredCategories"]) is not bool:
        errors.append("Cloudflare Adsterra unfiltered-category acceptance must be a boolean")
    if "datingExclusionConfirmed" in ad and type(ad["datingExclusionConfirmed"]) is not bool:
        errors.append("Cloudflare dating-category exclusion confirmation must be a boolean")
    if "automaticDisplay" in ad and type(ad["automaticDisplay"]) is not bool:
        errors.append("Cloudflare default advertising flag must be boolean")
    if "userAuthorizedTrial" in ad and type(ad["userAuthorizedTrial"]) is not bool:
        errors.append("Cloudflare explicit trial authorization must be a boolean")
    if ad.get("enabled") is True:
        filtered = (ad.get("siteStatus") == "approved" and
                    ad.get("allowUnfilteredCategories") is not True and
                    ad.get("gamblingExclusionConfirmed") is True and
                    ad.get("datingExclusionConfirmed") is True)
        trial = (ad.get("userAuthorizedTrial") is True and
                 ad.get("allowUnfilteredCategories") is True and
                 ad.get("siteStatus") in ("approved", "unverified"))
        if not (filtered or trial):
            errors.append("Cloudflare native requires verified category exclusions OR explicit documented unfiltered trial authorization")
    return errors

# Exact site-specific 320x50, 728x90, 300x250 Adsterra keys supplied by owner.
CLOUDFLARE_BANNERS = {
    'mobile': ('22d5d7312497a4575a8261d0d18522ea', 320, 50),
    'desktop': ('5b1925f1b2ab32ef7b6d207bde9e0fa1', 728, 90),
    'rectangle': ('58623b07e46a924f55b4d5d4895086c0', 300, 250),
}

def validate_cloudflare_banners(banners):
    if not isinstance(banners, dict):
        return ['cloudflareBanners must be an object']
    errors=[]
    if banners.get('websiteHost')!='jobpath-india.pages.dev':
        errors.append('Banner code must remain limited to the Cloudflare domain')
    if type(banners.get('enabled')) is not bool:
        errors.append('Banner enabled flag must be a boolean')
    if type(banners.get('deliveryVerified')) is not bool:
        errors.append('Banner source verification flag must be boolean')
    if banners.get('deliveryVerified') is True and banners.get('enabled') is not True:
        errors.append('Unenabled banners cannot claim verified delivery')
    units=banners.get('units')
    if not isinstance(units, dict) or set(units)!=set(CLOUDFLARE_BANNERS):
        return errors+['Expected exactly three distinct banner units']
    for name,(key,width,height) in CLOUDFLARE_BANNERS.items():
        u=units[name]
        if not isinstance(u,dict):
            errors.append(name+' must be a banner object')
            continue
        expected={'key':key,'width':width,'height':height,'format':'iframe','enabled':True,'scriptUrl':'https://bauval.org/22/'+key}
        if type(u.get('sourceVerified')) is not bool:
            errors.append(name+' sourceVerified must be boolean')
        for field,value in expected.items():
            if type(u.get(field)) is not type(value) or u.get(field)!=value:
                errors.append(name+' '+field+' differs from documented banner snippet')
    return errors

def validate(config):
    errors = []
    if not isinstance(config, dict):
        return ["Advertising config must be an object"]
    enabled = config.get("enabled")
    if not isinstance(enabled, bool):
        errors.append("enabled must be true or false")
        return errors
    provider = config.get("provider")
    publisher = config.get("publisherId", "")
    slots = config.get("slots", {})
    if not isinstance(slots, dict):
        return ["slots must be an object"]
    if "adsterra" in config:
        errors.extend(validate_adsterra(config["adsterra"]))
    if "cloudflareAdsterra" in config:
        errors.extend(validate_cloudflare_adsterra(config["cloudflareAdsterra"]))
    if "cloudflareBanners" in config:
        errors.extend(validate_cloudflare_banners(config["cloudflareBanners"]))
    if enabled:
        if provider == "adsense":
            if not isinstance(publisher, str) or not PUBLISHER_RE.fullmatch(publisher):
                errors.append("A real ca-pub- ID containing 16 digits is required")
            slot = slots.get("content")
            if not isinstance(slot, str) or not SLOT_RE.fullmatch(slot):
                errors.append("Real numeric in-content ad unit slot ID required")
        elif provider == "adsterra":
            ad = config.get("adsterra") if isinstance(config.get("adsterra"), dict) else {}
            if "adsterra" not in config:
                errors.extend(validate_adsterra(ad))
            if ad.get("siteStatus") != "approved" or ad.get("adUnitStatus") != "active":
                errors.append("Adsterra website approval and active unit are required")
            # Fail closed until the publisher has verified gambling/betting/casino
            # exclusion in the actual ad network account. A local config flag
            # alone does not prove that the network honors category filtering.
            if ad.get("gamblingExclusionConfirmed") is not True:
                errors.append("Adsterra gambling/betting/casino exclusion must be confirmed before enabling ads")
            consent = config.get("consent", {})
            if (not isinstance(consent, dict) or consent.get("required") is not True
                    or consent.get("version") != "adsterra-2026-10-30-trial"):
                errors.append("Versioned opt-in advertising consent is required")
            if publisher not in (None, "") or any(value not in (None, "") for value in slots.values()):
                errors.append("Adsterra must not use Google publisher or slot identifiers")
        else:
            errors.append("Only explicitly configured AdSense or Adsterra is supported")
    else:
        if provider != "none":
            errors.append("Disabled advertisements must use provider=none")
        if publisher not in (None, ""):
            errors.append("Do not store a publisher ID in disabled configuration")
        if any(value not in (None, "") for value in slots.values()):
            errors.append("Do not store ad slot IDs in disabled configuration")
    return errors


def load_and_validate():
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    errors = validate(config)
    if errors:
        raise ValueError("; ".join(errors))
    return config


if __name__ == "__main__":
    try:
        config = load_and_validate()
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"Advertising configuration INVALID: {exc}", file=sys.stderr)
        raise SystemExit(1)
    print("Advertising config valid: " + (config["provider"] + " configured; external account status must be checked" if config["enabled"] else "advertising disabled; no ad tracking script"))
