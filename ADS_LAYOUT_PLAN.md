# JOBPATH INDIA: professional responsive ad placements

Owner screenshots (31 October 2026) identify three separate banners belonging to jobpath-india.pages.dev:

- Mobile 320x50: 22d5d7312497a4575a8261d0d18522ea
- Desktop 728x90: 5b1925f1b2ab32ef7b6d207bde9e0fa1
- 300x250 Rectangle: 58623b07e46a924f55b4d5d4895086c0
- Existing Native Banner: 84de856c9d01a37c08d4912fb3df530

Layout: top immediately before hero = responsive 728x90 desktop OR 320x50 mobile; middle after Explore by career path tiles = 300x250; bottom immediately after Examination resources and before footer = existing Native Banner. No ad stacks or fixed overlays.

Privacy: all banner iframes and native tags are embedded only for an explicitly opted-in visitor on the exact Cloudflare host. The footer lets people withdraw. Other sites and AdSense are unchanged.

LIMITATION: screenshots show exact atOptions keys and mobile banner script prefix https://bauval.org/22/ but full script URLs for each size are cropped. This implementation reconstructs URLs as https://bauval.org/22/<key> and should be checked against the complete copied Adsterra tags. Build/test success does not imply actual ad fill.

Adsterra support has filtered advertisers involved in a dating-ad complaint, but comprehensive exclusions are not confirmed. Ads may still contain inappropriate creatives. Verify network-side settings before declaring the site dating-free.

Static build: scripts/build_dist.py creates dist/ad-units/mobile.html, desktop.html and rectangle.html from strictly validated configuration. The third-party atOptions scripts are each isolated in a sandboxed iframe. These wrappers are not referenced without opt-in.


## Empty inventory handling
The mobile, desktop and rectangle iframe banners now report actual rendered creative markup to the parent. The parent validates the report's iframe window identity and collapses an empty/error unit after its viewport-visible timeout. A provider script that returns no creative must not leave a permanent white 320x50/300x250/728x90 slot. This is a best-effort indicator, not independent live ad-delivery verification. The working Native Banner is unchanged.
