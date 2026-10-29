"""Select the public HTTPS origin at build time without changing ad approval."""
import os
import re
from urllib.parse import urlsplit

DEFAULT_SITE_URL = "https://jobpath-india.netlify.app"


def site_origin(environ=None):
    env = os.environ if environ is None else environ
    value = env.get("JOBPATH_SITE_URL", "")
    if not value and env.get("RENDER") == "true":
        value = env.get("RENDER_EXTERNAL_URL", "")
    value = value or DEFAULT_SITE_URL
    # Only a public HTTPS origin is useful for canonical/OG/schema/sitemap URLs.
    # Reject credentials, paths and markup rather than publish broken metadata.
    if not isinstance(value, str) or re.search(r"[\s<>\"'\\]", value):
        raise ValueError("Site URL must be a public HTTPS origin without credentials or a path")
    try:
        parsed = urlsplit(value)
        host = parsed.hostname or ""
        valid_host = re.fullmatch(r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z][a-z0-9-]{0,62}", host)
        valid = (parsed.scheme == "https" and valid_host and not parsed.username
                 and not parsed.password and parsed.port is None
                 and parsed.path in ("", "/") and not parsed.query
                 and not parsed.fragment and "?" not in value and "#" not in value)
    except ValueError:
        valid = False
    if not valid:
        raise ValueError("Site URL must be a public HTTPS origin without credentials or a path")
    return "https://" + host
