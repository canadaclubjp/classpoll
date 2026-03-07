# ClassPoll

[![Open in VS Code](https://img.shields.io/badge/Open%20in-VS%20Code-007ACC?logo=visualstudiocode&logoColor=white)](https://vscode.dev/github/canadaclubjp/classpoll)

An anonymous in-class poll/survey web app built with Flask + SQLAlchemy, designed for ~35–50 students scanning a QR code. Polls expire after 24 hours and support multiple-choice and short-text questions.

## Features

- **Anonymous** – no student identity collected; one response per device/browser via a per-poll cookie.
- **Editable** – students can update their response until the poll closes.
- **Poll types** – multiple-choice (required) and short-text (optional), 2–5 questions per poll.
- **Admin UI** – create, open/close, view results, display QR code, and delete polls.
- **QR code** – server-side PNG generated for each poll's student URL.
- **24-hour retention** – polls and all related data auto-expire; a CLI command prunes them.
- **Fly.io ready** – Dockerfile, Procfile, and `PORT` env var support.

---

## Local Development

### Prerequisites

- Python 3.10+
- PostgreSQL **or** SQLite (SQLite is used automatically when `DATABASE_URL` is not set)

### Setup

```bash
# 1. Clone & enter the repo
git clone https://github.com/canadaclubjp/classpoll.git
cd classpoll

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env – set ADMIN_TOKEN (required), DATABASE_URL (optional for SQLite)

# 5. Run the development server
flask --app wsgi run --debug
```

The app will be available at **http://localhost:5000**.

Admin dashboard: `http://localhost:5000/admin/<ADMIN_TOKEN>`

---

## Flask CLI Commands

```bash
# Delete all expired polls and their related data
flask --app wsgi purge-expired
```

Schedule this command as a cron job (e.g., every hour) in production.

---

## Database Migrations

Flask-Migrate is included for schema management:

```bash
flask --app wsgi db init      # first time only
flask --app wsgi db migrate -m "initial"
flask --app wsgi db upgrade
```

---

## Deploying to Fly.io

### Prerequisites

- [Fly CLI](https://fly.io/docs/getting-started/installing-flyctl/) installed and authenticated.
- A Fly.io account.

### Steps

```bash
# 1. Launch the app (creates fly.toml)
fly launch --name classpoll --region nrt

# 2. Create a Postgres database
fly postgres create --name classpoll-db --region nrt
fly postgres attach --app classpoll classpoll-db

# 3. Set required secrets
fly secrets set ADMIN_TOKEN="$(openssl rand -hex 32)"
fly secrets set SECRET_KEY="$(openssl rand -hex 32)"

# 4. Deploy
fly deploy

# 5. Run migrations (if using Flask-Migrate)
fly ssh console -C "flask --app wsgi db upgrade"
```

### Scheduled purge

Add a cron-style Fly Machine or use `fly cron` (if available) to run `flask --app wsgi purge-expired` hourly.

---

## Environment Variables

| Variable       | Required | Default        | Description                                      |
|----------------|----------|----------------|--------------------------------------------------|
| `ADMIN_TOKEN`  | Yes      | `changeme`     | Secret token for the admin interface URL         |
| `DATABASE_URL` | No       | SQLite (local) | PostgreSQL connection string                     |
| `SECRET_KEY`   | No       | `dev-secret-change-me` | Flask session signing key             |
| `PORT`         | No       | `8080`         | Port for gunicorn / dev server                   |

---

## Project Structure

```
classpoll/
├── app/
│   ├── __init__.py        # create_app(), Flask CLI commands
│   ├── models.py          # SQLAlchemy models
│   ├── routes_admin.py    # Admin Blueprint
│   └── routes_student.py  # Student Blueprint
├── templates/
│   ├── base.html
│   ├── admin/
│   │   ├── dashboard.html
│   │   ├── create_poll.html
│   │   ├── poll_detail.html
│   │   └── results.html
│   └── student/
│       ├── poll.html
│       ├── submitted.html
│       └── expired.html
├── wsgi.py
├── requirements.txt
├── Dockerfile
├── Procfile
└── .env.example
```
