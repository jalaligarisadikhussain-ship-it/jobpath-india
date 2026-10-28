# JOBPATH INDIA — One-time GitHub + Netlify setup for daily monitoring

## What will happen automatically?

- Every day at **07:45 IST**, GitHub Actions checks selected recruitment-organization web pages.
- If a source page changes, it records **possible changes for review** in `reports/source-watch-latest.md` and the Actions run summary. A changed webpage does **not** prove a new vacancy.
- A human opens the official notice PDF, cross-checks dates, eligibility, counts, notification ID, official application link, and changes `data/jobs.json` only if verified.
- Once the GitHub repository is linked to the existing Netlify **jobpath-india** site, **each reviewed GitHub update is deployed automatically**. No daily ZIP uploads.
- Existing job application deadlines use local browser date to display expired jobs as Closed **without a new deployment**.
- This doesn't automatically discover, extract, and fact-check every new government job. Official websites often use JS, CAPTCHA, PDFs and login-dependent pages. Their availability or content hash may fluctuate.

## Step 1 — Create a *new*, separate GitHub repo (GitHub Desktop)

1. Extract `JOBPATH_INDIA_GITHUB_DAILY_AUTO_UPDATE_SOURCE.zip` locally. The root contains `index.html`, `data/`, `scripts/`, `.github/`, `assets/` and `netlify.toml`.
2. Open **GitHub Desktop** (free). Go to **File → Add local repository** and select the extracted folder. If it says it is not a repository, choose **Create a repository here**.
3. Commit the new files and click **Publish repository**. Name it `jobpath-india` under your GitHub account. This automatically creates a **new repository**, separate from ByteBright. Do not try to publish over a repository that already exists.
4. Make sure the hidden `.github/workflows/` directory is included. Check GitHub repo → **Actions** for the `Daily government-recruitment source watch` workflow. Enable workflows if asked.
5. **Alternative for Git CLI users:** create an empty `jobpath-india` repository on GitHub first, then run the commands below inside the extracted source folder.

Example CLI for the *new* folder only (run after creating the empty GitHub repo):

```powershell
cd "C:\path\to\jobpath-india-auto-update"
git init
git add .
git commit -m "Initial JobPath India version with daily source watch"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/jobpath-india.git
git push -u origin main
```

## Step 2 — One-time connect existing Netlify project

1. Open https://app.netlify.com/projects/jobpath-india . Confirm it is **jobpath-india**, not ByteBright.
2. Look for **Project configuration** → **Build & deploy** → **Continuous deployment** → **Link repository**. (Netlify settings labels can vary.)
3. Choose GitHub, authorize only the new `jobpath-india` repo as needed, select branch `main`.
4. Site build command: `python3 scripts/build_dist.py`. Publish directory: `dist` (only public static files; automation and internal review reports are not published). This is a static site; do not enable paid build plugins.
5. Keep the existing Netlify project and its `jobpath-india.netlify.app` URL. Check for "Published" and inspect the site after the first Git deploy.
6. Verify that `https://jobpath-india.netlify.app/googlefcd24aba957dc07b.html` still loads and Google Search Console property stays verified.

## Step 3 — Test the schedule immediately

- GitHub repo → **Actions** → **Daily government-recruitment source watch** → **Run workflow**.
- First run records a fingerprint **baseline** for accessible official pages and may mark some sources **unreachable** due to anti-bot blocking. This is expected; unreachable does not mean no recruitment.
- Subsequent runs identify changed-page leads; review them before publishing.
- The scheduled job generally runs daily, but GitHub can delay scheduled workflows or disable schedules after prolonged repository inactivity. Check the Actions tab occasionally.
- Free-tier usage limits apply to both GitHub Actions and Netlify builds. Source checks are lightweight and should not be used to flood government websites.

## Adding a *verified* job without manual ZIPs

1. Open the official recruitment notice and its official application link.
2. Edit `data/jobs.json` in GitHub with correct ISO dates and validated fields, using an existing verified job as a template.
3. Run tests (GitHub Actions or locally `npm test && npm run validate`).
4. Commit to `main`. Netlify builds and publishes the updated website automatically. For greater safety, use a pull request and merge after review.
5. If government notice changed, correct existing record and its verification date. Never automatically mark a new job Open merely because a page was updated.

## Safety and limitations

- The monitoring workflow does **not** write to `data/jobs.json` or invent vacancy information.
- No API keys, external paid services, Netlify deploy tokens, or administrator passwords are required in source control.
- GitHub auto-deploy requires a **one-time** GitHub repo link to the existing Netlify site, which is not yet configured by generating this package.
- The cron runs on GitHub's UTC clock; 02:15 UTC equals 07:45 IST year-round.
- `reports/source-watch-latest.md` is a source-change signal, not government confirmation of any notification.
- Source-page monitoring may produce false positives or miss PDF changes. Manual review is necessary before announcing deadlines, vacancies, or application links.
