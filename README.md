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

> **Important:** Railway deploys from whichever branch you select. Make sure you are deploying from a branch that contains the app files (`main.py`, `requirements.txt`, `start.sh`). The safest approach is to merge this PR into `main` first, then connect Railway to `main`.

**Step-by-step:**

1. Merge this PR (or the branch containing the app code) into `main` on GitHub.
2. Create a free account at https://railway.app.
3. In the Railway dashboard click **New Project → Deploy from GitHub repo** and connect this repository.
4. When prompted, select **`main`** as the deployment branch (or whichever branch you merged the app code into).
5. Railway will detect the `railway.toml` in the repo and use the correct build and start commands automatically — no further configuration is needed.
6. Once deployed, Railway gives you a public URL like `https://classpoll-production.up.railway.app`. Use that URL in your QR codes.

**If you already have a Railway project connected and it is failing:**

1. Go to your Railway project → **Settings → Source**.
2. Confirm the **Branch** field is set to `main` (or the branch that has `main.py` and `requirements.txt`).
3. Trigger a new deploy.

**Free tier:** 500 hours/month — more than enough for classroom use.

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

