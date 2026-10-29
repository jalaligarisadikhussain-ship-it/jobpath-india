"""Public Google AdSense ownership signals; never turns on ad serving by itself.

The account ID was supplied by the owner's AdSense dashboard and confirmed by
Google AdSense's welcome email dated 28 October 2026.
"""
PUBLISHER_ID = "pub-8073443569494348"
ADSENSE_ACCOUNT_ID = "ca-" + PUBLISHER_ID
ADSENSE_META_TAG = f'<meta name="google-adsense-account" content="{ADSENSE_ACCOUNT_ID}">'
ADS_TXT_LINE = f'google.com, {PUBLISHER_ID}, DIRECT, f08c47fec0942fa0\n'
