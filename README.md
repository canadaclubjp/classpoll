# Classpoll

A simple classroom poll web app built with Python and Flask.  
Teachers can create live polls, students vote in their browser, and results are shown as a live bar chart.

---

## Project files

```
classpoll/
├── main.py            # Flask application – routes and logic
├── poll.py            # Poll data model (in-memory store)
├── requirements.txt   # Python dependencies
└── templates/
    ├── index.html     # Home page – list all polls
    ├── create.html    # Create a new poll
    ├── poll.html      # Voting page
    └── results.html   # Results page
```

---

## Quick start (PyCharm or any terminal)

### 1. Clone or download the repository

Download the ZIP from GitHub and unzip it, or clone it:

```bash
git clone https://github.com/canadaclubjp/classpoll.git
cd classpoll
```

### 2. Create and activate a virtual environment (recommended)

**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS / Linux**
```bash
python3 -m venv venv
source venv/bin/activate
```

> In PyCharm you can also do: *File → Settings → Project → Python Interpreter → Add → Virtual Environment → OK*.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
python main.py
```

Open **http://127.0.0.1:5000** in your browser.

> **Production tip:** set the `SECRET_KEY` environment variable before running:
> ```bash
> export SECRET_KEY="your-random-secret-here"   # macOS / Linux
> set SECRET_KEY=your-random-secret-here         # Windows cmd
> ```
> To enable debug/reload mode during development, also set `FLASK_DEBUG=1`.

---

## Usage

| Page | URL |
|---|---|
| Home (all polls) | `http://127.0.0.1:5000/` |
| Create a poll | `http://127.0.0.1:5000/create` |
| Vote on a poll | `http://127.0.0.1:5000/poll/<id>` |
| View results | `http://127.0.0.1:5000/results/<id>` |

1. Click **+ New Poll** to create a question with 2–6 answer options.  
2. Share the vote link with students (or display it on a projector).  
3. Click **View Results** at any time to see the live bar chart.  
4. Use **Close Poll** to stop voting, **Reset Votes** to start over, or **Delete** to remove the poll.

> **Note:** Polls are stored in memory. They will be lost when the server is restarted.  
> For persistent storage, the `poll.py` module can be extended with a database (e.g., SQLite via Flask-SQLAlchemy).

---

## Requirements

- Python 3.10 or newer  
- Flask 2.3 or newer (installed automatically by `pip install -r requirements.txt`)
