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
            consent = config.get("consent", {})
            if (not isinstance(consent, dict) or consent.get("required") is not True
                    or consent.get("version") != "adsterra-2026-10-29"):
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
