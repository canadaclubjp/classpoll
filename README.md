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

> **Important:** Railway deploys from whichever branch you select. The app files (`main.py`, `requirements.txt`, etc.) currently live on a pull-request branch, not on `main`. You must merge that pull request into `main` first, then connect Railway.

#### Step 1 — Merge the pull request into `main`

1. Go to your repository on GitHub: https://github.com/canadaclubjp/classpoll
2. Click the **Pull requests** tab near the top of the page.
3. Click on the open pull request in the list (the one that adds the app files).
4. Scroll to the bottom of the pull request page until you see a green **"Merge pull request"** button.
5. Click **"Merge pull request"**, then click **"Confirm merge"**.
6. `main` now contains the app files.

> **Note:** If you clicked a "View pull request" button in a GitHub notification email or on the Issues tab, that takes you to the pull request page — just keep scrolling down on that page until you find the green **"Merge pull request"** button at the bottom.

#### Step 2 — Deploy on Railway

1. Create a free account at https://railway.app.
2. In the Railway dashboard click **New Project → Deploy from GitHub repo** and connect this repository (`canadaclubjp/classpoll`).
3. When prompted, make sure the **Branch** is set to **`main`**.
4. Railway will detect the `railway.toml` file and use the correct build and start commands automatically — no further configuration needed.
5. Once deployed, Railway gives you a public URL like `https://classpoll-production.up.railway.app`. Use that URL in your QR codes.

**If you already have a Railway project connected and it is failing:**

1. Go to your Railway project → **Settings → Source**.
2. Confirm the **Branch** field is set to `main`.
3. Click **Deploy** to trigger a new build.

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

