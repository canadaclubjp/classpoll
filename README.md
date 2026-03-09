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

1. Create a free account at https://railway.app
2. In the Railway dashboard click **New Project → Deploy from GitHub repo** and connect this repository.
3. Railway will auto-detect Python and deploy the app. No configuration file is needed.
4. Once deployed, Railway gives you a public URL like `https://classpoll-production.up.railway.app`. Use that URL in your QR codes.

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

