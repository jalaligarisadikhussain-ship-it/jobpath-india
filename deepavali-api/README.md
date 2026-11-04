# Deepavali Dhamaka — tracking preview backend

The free-spin gift wheel remains a **DEMO**. This backend stores voluntary participant registrations and reviewer-decided referral/group-proof statuses. It does **not** issue coupons, payments or real prizes.

## Architecture / privacy

- Public wheel: `https://deepavali-dhamaka-spin-2026.onrender.com/` (Render Static Site; Adsterra Social Bar only). No registration required. Anonymous referral browser-play progress (not verified people) and approved group screenshot review progress appear only after the backend is connected.
- Anonymous private group proof submission: `https://deepavali-dhamaka-tracking-api.onrender.com/proof` on the ad-free Render API origin. Viewer opens from public wheel using an opaque, temporary private URL fragment after tracking session starts.
- Private admin: `https://deepavali-dhamaka-tracking-api.onrender.com/admin` (password + signed, HttpOnly, Secure, SameSite=Strict admin session; 8-hour expiry).
- Legacy registered participant credentials remain on the ad-free API origin. For the **registration-free anonymous mode**, a random browser tracking token resides in localStorage on the public wheel and is passed only via a URL fragment to the ad-free proof page. Third-party ads on the wheel may be capable of reading browser storage: never use this anonymous token for sensitive identity, money, or financial actions. Private group screenshots are sent directly to the separate API origin; no images/emails/phone numbers are exposed by public counting endpoints.
- Render Postgres `deepavali-dhamaka-tracking-db` stores registrations (name/email, invite relationship, random session-token hash) and at most five screenshots per member, private to the admin.
- Legacy admin registrations still support manual verified statuses. Registration-free mode uses distinct browser-token **first-spin engagements** as approximate visitor counts, not manually verified humans or WhatsApp messages; up to five group-proof screenshots per browser can be privately approved/rejected by the organizer. Approval is a review status, not WhatsApp delivery verification.
- Browsers can delete their own registration and related proof images from Join & Track. Admin can delete individual proof images.
- Social Bar remains enabled on wheel, Popunder and Native Banner disabled. Tracking does **not** depend on ad views/clicks.

## Registration-free mode (November 4, 2026)

- Public spin page requests `POST /api/anon/start` and locally stores an opaque browser token. Your unique `?ref=SPIN-...` URL is then used for WhatsApp invitations without requiring recipients to register.
- A referred **browser** counts only after it actually starts its first spin (`POST /api/anon/play`). The same browser token is counted once and associated with at most one inviter. Bot/browser resets may still fake distinct browsers; NEVER label these as verified unique humans or messages delivered.
- Viewers can see their **own** 0/20 browser-play count and 0/5 organizer-reviewed group-screenshot count; no private data is publicly retrievable by referral code.
- Proof upload is on `/proof` (ad-free API origin) with PNG/JPEG/WebP images below 900 KB, client-side compression, redaction/consent, distinct group labels, max five. An authenticated admin reviews proof images under `/admin/api/anon-proofs`.
- `DATABASE_URL` must point to Render Postgres before this can store data. Both counters remain unavailable if DB is not connected. Free DB expires on December 4, 2026.
- Don't put anything sensitive in public wheel localStorage; anonymous token can potentially be read by third-party scripts and therefore cannot serve as a strong identity credential.
- Prizes are illustrative only; Adsterra Social Bar ON, Native Banner and Popunder OFF.

## First-time Render configuration (private, do not paste connection URL into ChatGPT)

The Render **free** Postgres created 4 November 2026 has a scheduled expiration **4 December 2026**. Move to a durable database before that date; otherwise records can be lost. Don't launch a prize promotion depending on this temporary storage.

1. Open the Render Postgres **deepavali-dhamaka-tracking-db** dashboard and copy its **Internal Database URL** under Connections. Keep this connection string secret.
2. Open the **deepavali-dhamaka-tracking-api** Render web-service dashboard → Environment → Add Environment Variable `DATABASE_URL` = that internal URL. Save and redeploy. Both services are in Singapore. Do not place this value in GitHub.
3. The web-service Environment should also contain `ADMIN_PASSWORD` (long random password), `ADMIN_SESSION_SECRET` (32+ random characters), `NODE_ENV=production`, and `FRONTEND_ORIGIN=https://deepavali-dhamaka-spin-2026.onrender.com`. The password is shown/managed **only in your Render dashboard**; rotate it after initial setup.
4. Check `https://deepavali-dhamaka-tracking-api.onrender.com/healthz` returns `{"status":"ok","database":"connected","prizes":"demo only"}`. If not, do not claim verified tracking works.
5. Test one **genuine, consented** registration from the Join & Track page. It must show pending. Then log in to /admin and verify the record only after independent human checks. The inviter's verified counter must update from the server.
6. Upload only **redacted** test proof images with consent, approve one manually in admin, then check the account's group review count. Delete test account/data afterwards.
7. Before any public collection of real participant data, publish organizer privacy contact, data retention schedule, privacy/legal review and data recovery plan. No auto-email verification, CAPTCHA, hard identity proof, or audit-grade WhatsApp verification exists.

## Endpoints

- `GET /healthz` – real database connection check.
- `GET /api/config` – tracking-ready flag, prize-disabled flag.
- `POST /api/enroll` – consented registration; returns an unguessable participant token.
- `GET /api/me` – participant's pending/verified counts, requires their bearer token.
- `POST /api/proofs` – max five distinct group labels, image under 900 KB, token and consent required.
- `DELETE /api/me` – participant-owned account and proof deletion.
- Verified referral counts and group-proof review totals are exclusively exposed by password-protected `/admin/api/*` endpoints. Public `/api/public-counts/:code` has been disabled; the visitor enrollment page does not display any verification statistics.
- `/admin` and `/admin/api/*` – authenticated review and private image access.

## Deployment

- Render static site autoDeploy was previously unreliable; check actual `live` status before announcing changes.
- The Render API web service has autoDeploy disabled. Trigger a manual deploy after committing the backend.
- Startup uses `npm --prefix deepavali-api install --omit=dev` and `npm --prefix deepavali-api start`.
- Free service can sleep, so initial page load may be slower. A loaded Adsterra script is not proof a creative was displayed.
