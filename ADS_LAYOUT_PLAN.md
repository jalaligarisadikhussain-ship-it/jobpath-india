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


### White ad-frame corrective patch
The previous fill checker incorrectly treated any nested iframe as a successful ad. A cross-origin iframe can be completely white or unfilled. That shortcut is removed. Only positively visible images, canvas/video creatives or substantial visible text can make the parent keep the banner; otherwise the slot collapses within about 5–6 seconds after entering the viewport. This conservatively hides iframe-only ad formats that cannot be inspected; it prioritizes removing blank placements over maximizing impressions. Full publisher script code and real delivery still need verification for the top/middle formats; the known working native slot is not changed.


## 31 October 2026: fail-closed correction for the screenshot's empty advertisement
Both fixed banner regions are paused until original **complete** Adsterra script sources can be read from the publisher's Copy Code dialogs. This prevents ad iframe requests to reconstructed URLs and entirely removes the resulting blank top/middle boxes on all future deployed builds. The working Cloudflare-specific Native Banner remains at the bottom, subject to the same visitor consent. The codes remain recorded; they have not been discarded. To restore three positions, verify the exact full `<script src>` tags, then explicitly set `cloudflareBanners.deliveryVerified=true` only after testing that those exact URLs render. Do not claim top/middle ad revenue is active while the units are paused.


### Mobile banner code received (October 31, 2026)
The owner supplied the entire Adsterra 320×50 script with exact key `22d5d7312497a4575a8261d0d18522ea`, iframe format and script `https://bauval.org/22/22d5d7312497a4575a8261d0d18522ea`. These **source parameters** are now verified. This does **not** independently confirm a successful ad response. The mobile homepage uses an opt-in-only trial with blank-collapse protection. Desktop 728×90 and rectangle 300×250 remain unpublished until exact complete tags are supplied. Native bottom banner remains enabled.


### All three banner tags received on October 31, 2026
The owner supplied the **complete** 728×90 desktop and 300×250 rectangle tags, in addition to the mobile 320×50. All three existing keys, sizes and complete `https://bauval.org/22/{key}` source URLs match the source configuration. The three banner units are now code-verified and rendered in sandboxed separate HTML wrappers, consent-gated and host-restricted. Homepage top shows one device-appropriate banner (320×50 mobile or 728×90 desktop). Middle shows 300×250. Existing native placement stays at bottom. Adsterra ad delivery/creative suitability have not been independently verified; empty-fill auto-hide is best effort.


## 31 October — confirmed blank-probe JavaScript syntax bug
The old `build_dist.py` generated a single-line probe snippet containing `//` comments. These comments swallowed the remaining JavaScript source (including closing braces), so the monitoring script was invalid and no `jobpath-banner-fill` event could be delivered. Replaced the inline line-comments with a block comment, cache-busted JS/CSS/ad iframe documents and added a production regression check running `node --check -` against BOTH generated inline scripts in each ad HTML document. This repairs the fill-status reporting path, not the external Adsterra inventory. Ads may remain unfilled/blocked by browsers or the network. On missing fill the existing parent watchdog hides the blank unit. The standalone native script remains unchanged.


## Native empty-slot safety guard
The native unit is now monitored after a consented request. If neither substantial image/video/canvas content nor text-bearing ad links appear after eight seconds, the entire native panel is hidden (including the ADVERTISEMENT header). An existing creative stays visible. This complements the repaired top/middle banner probe. Third-party cross-origin iframe contents cannot be reliably inspected, so provider-side no-fill or browser blocking may still limit real impressions.
