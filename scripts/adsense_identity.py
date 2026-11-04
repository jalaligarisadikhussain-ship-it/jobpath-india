"""Public Google AdSense ownership signals; never turns on ad serving by itself.

The new account ID is taken from the owner's AdSense site-verification screen
on 4 November 2026. This is an ownership signal only, not ad approval.
"""
PUBLISHER_ID = "pub-4312394725152098"
ADSENSE_ACCOUNT_ID = "ca-" + PUBLISHER_ID
ADSENSE_META_TAG = f'<meta name="google-adsense-account" content="{ADSENSE_ACCOUNT_ID}">'
ADS_TXT_LINE = f'google.com, {PUBLISHER_ID}, DIRECT, f08c47fec0942fa0\n'
