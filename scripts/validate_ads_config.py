#!/usr/bin/env python3
"""Validate public AdSense configuration. Fail closed on missing/invalid IDs."""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "data" / "ads-config.json"
PUBLISHER_RE = re.compile(r"ca-pub-[0-9]{16}\Z")
SLOT_RE = re.compile(r"[0-9]{8,12}\Z")


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
    if enabled:
        if provider != "adsense":
            errors.append("Only an explicitly configured AdSense provider is supported")
        if not isinstance(publisher, str) or not PUBLISHER_RE.fullmatch(publisher):
            errors.append("A real ca-pub- ID containing 16 digits is required")
        slot = slots.get("content")
        if not isinstance(slot, str) or not SLOT_RE.fullmatch(slot):
            errors.append("Real numeric in-content ad unit slot ID required")
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
    print("Advertising config valid: " + ("AdSense placement configured (external approval not verified)" if config["enabled"] else "advertising disabled; no ad tracking script"))
