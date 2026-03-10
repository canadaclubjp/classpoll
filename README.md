# Classpoll

A simple classroom poll app built with Flask.

## Running locally

```bash
pip install -r requirements.txt
python main.py
```

Then open http://localhost:5000 in your browser.

---

## Free hosting (run without your home computer)

If you want to create a poll at home, then use it from your iPad at university without keeping your computer on, you need to host the app on a free cloud service. Here are two easy options:

---

### Option A — Railway (recommended, easiest)

> **Already deployed Railway but the public URL does not open the app?**  
> See the **[Railway URL not opening — fix](#railway-url-not-opening--fix)** section below.

#### Step 1 — Merge the right pull request into `main`

There may be several open pull requests in this repository. **Only merge this one** (titled "README: explain Draft PR → Ready for review → Merge flow", PR #4). The others are listed below — you can leave them open or close them, but **do not merge them**:

| PR | Title | What it does | Merge? |
|----|-------|--------------|--------|
| #1 | Fix "Open in VS Code" button | Adds VS Code dev-container config — only useful if you edit code in VS Code | **No** |
| #3 | Add SQLite persistence and QR sharing | Duplicate of features already in the app — would conflict | **No** |
| #4 | README: explain Draft PR flow *(this one)* | Adds `railway.toml` so Railway uses the correct port | **Yes** |

To merge PR #4:

1. Go to your repository on GitHub: https://github.com/canadaclubjp/classpoll
2. Click the **Pull requests** tab near the top of the page.
3. Click on the pull request titled **"README: explain Draft PR → Ready for review → Merge flow"** (PR #4).
4. Near the bottom of the pull request page you will see a grey **"Ready for review"** button — click it.  
   *(The pull request was created as a Draft, which is why you see "Ready for review" instead of "Merge pull request". Converting it to ready unlocks the merge button.)*
5. After clicking "Ready for review", the page refreshes and shows a green **"Merge pull request"** button at the bottom.
6. Click **"Merge pull request"**, then click **"Confirm merge"**.
7. `main` now contains the `railway.toml` file that fixes the Railway URL.

> **Note:** If you see a "View pull request" button (e.g. in a GitHub notification email), click it — that takes you directly to the pull request page where you can follow the "Ready for review" and "Merge pull request" steps above.

#### Step 2 — Deploy on Railway

1. Create a free account at https://railway.app.
2. In the Railway dashboard click **New Project → Deploy from GitHub repo** and connect this repository (`canadaclubjp/classpoll`).
3. When prompted, make sure the **Branch** is set to **`main`**.
4. Railway will detect the `railway.toml` file and use the correct build and start commands automatically — no further configuration needed.
5. The app requires one environment variable — set `ADMIN_TOKEN` to any secret phrase you choose (e.g. `mysecret123`). In Railway, go to your service → **Variables** → **New Variable** → add `ADMIN_TOKEN` = your chosen value.
6. Once deployed, Railway gives you a public URL like `https://classpoll-production.up.railway.app`. Use that URL in your QR codes.
7. Access the admin dashboard at: `https://your-railway-url/admin/YOUR_ADMIN_TOKEN`

**If you already have a Railway project connected and it is failing:**

1. Go to your Railway project → **Settings → Source**.
2. Confirm the **Branch** field is set to `main`.
3. Click **Deploy** to trigger a new build.

**Free tier:** 500 hours/month — more than enough for classroom use.

---

#### Railway URL not opening — fix

**Symptom:** Railway shows the deployment as successful and Settings → Networking shows Port 8080, but clicking the public URL shows an error or blank page.

**Cause:** The app's `Dockerfile` starts gunicorn on a hardcoded port. Railway injects its own `$PORT` variable and routes the public domain to that port. If they don't match, the URL cannot reach the app.

**Fix:** Merge PR #4 (this pull request). It adds a `railway.toml` file that tells Railway to start the app with `--bind 0.0.0.0:$PORT`, so the port always matches what Railway expects. After merging, Railway will automatically redeploy and the URL will open correctly.

**Verify:** After redeployment, in Railway go to **Deployments** → click the latest deployment → check the logs. You should see a line like:  
`Listening at: http://0.0.0.0:XXXX (1234)`  
(where XXXX is the port Railway assigned). If the app starts successfully, the public URL will work within a few seconds.

---

### Option B — Render

1. Create a free account at https://render.com
2. Click **New → Web Service** and connect this GitHub repository.
3. Set the following:
   - **Runtime:** Python 3
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn main:app`
4. Click **Deploy**. Render gives you a public URL like `https://classpoll.onrender.com`.

> **Note:** Render free-tier web services spin down after 15 minutes of inactivity and take ~30 seconds to wake up on the next request. This is fine for classroom use — just open the app before class.

**Free tier:** 750 hours/month.

---

### Persistent database note

Both Railway and Render offer free deployments with an **ephemeral filesystem** — meaning the SQLite `polls.db` file is reset whenever the service restarts or redeploys. For a permanent database, add a free **PostgreSQL** add-on from either platform, then update `main.py` to use the `DATABASE_URL` environment variable. This is optional; for most classroom use the ephemeral database is perfectly fine as long as you do not redeploy mid-session.

