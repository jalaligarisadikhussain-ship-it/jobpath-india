# JOBPATH INDIA: professional responsive ad placements

Owner screenshots (31 October 2026) identify three separate banners belonging to jobpath-india.pages.dev:

- Mobile 320x50: 22d5d7312497a4575a8261d0d18522ea
- Desktop 728x90: 5b1925f1b2ab32ef7b6d207bde9e0fa1
- 300x250 Rectangle: 58623b07e46a924f55b4d5d4895086c0
- Existing Native Banner: 84de856c9d01a37c08d4912fb3df530

Layout: after homepage hero, one responsive banner (desktop 728x90 OR mobile 320x50); after latest vacancies, 300x250; after official sources, the single native banner. No duplicated native container and no fourth intrusive slot.

Privacy: all banner iframes and native tags are embedded only for an explicitly opted-in visitor on the exact Cloudflare host. The footer lets people withdraw. Other sites and AdSense are unchanged.

LIMITATION: screenshots show exact atOptions keys and mobile banner script prefix https://bauval.org/22/ but full script URLs for each size are cropped. This implementation reconstructs URLs as https://bauval.org/22/<key> and should be checked against the complete copied Adsterra tags. Build/test success does not imply actual ad fill.

Adsterra support has filtered advertisers involved in a dating-ad complaint, but comprehensive exclusions are not confirmed. Ads may still contain inappropriate creatives. Verify network-side settings before declaring the site dating-free.

Static build: scripts/build_dist.py creates dist/ad-units/mobile.html, desktop.html and rectangle.html from strictly validated configuration. The third-party atOptions scripts are each isolated in a sandboxed iframe. These wrappers are not referenced without opt-in.
