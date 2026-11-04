# Deepavali Dhamaka — tracking preview backend

The free-spin gift wheel remains a **DEMO**. This backend stores voluntary participant registrations and reviewer-decided referral/group-proof statuses. It does **not** issue coupons, payments or real prizes.

## Architecture / privacy

- Public wheel: `https://deepavali-dhamaka-spin-2026.onrender.com/` (Render Static Site; Adsterra Social Bar only).
- Participant enrollment: `https://deepavali-dhamaka-tracking-api.onrender.com/join` (separate Render Node service, no third-party ads).
- Private admin: `https://deepavali-dhamaka-tracking-api.onrender.com/admin` (password + signed, HttpOnly, Secure, SameSite=Strict admin session; 8-hour expiry).
- Private participant token is stored **only on the API origin**, never on the ad-supported wheel's origin. The public wheel sees a shareable code and queries counts only, **not emails or images**.
- Render Postgres `deepavali-dhamaka-tracking-db` stores registrations (name/email, invite relationship, random session-token hash) and at most five screenshots per member, private to the admin.
- Admin can mark registrations `pending / verified / rejected`, and each group screenshot `pending / approved / rejected`; referral totals count only participants marked verified. Screenshots alone do not objectively prove WhatsApp delivery or group uniqueness.
- Browsers can delete their own registration and related proof images from Join & Track. Admin can delete individual proof images.
- Social Bar remains enabled on wheel, Popunder and Native Banner disabled. Tracking does **not** depend on ad views/clicks.

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
- `GET /api/public-counts/:code` – aggregate-only counters; no personal data or tokens.
- `/admin` and `/admin/api/*` – authenticated review and private image access.

## Deployment

- Render static site autoDeploy was previously unreliable; check actual `live` status before announcing changes.
- The Render API web service has autoDeploy disabled. Trigger a manual deploy after committing the backend.
- Startup uses `npm --prefix deepavali-api install --omit=dev` and `npm --prefix deepavali-api start`.
- Free service can sleep, so initial page load may be slower. A loaded Adsterra script is not proof a creative was displayed.
