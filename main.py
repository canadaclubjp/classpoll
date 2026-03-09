import io
import sqlite3
import uuid

import qrcode
from flask import Flask, redirect, render_template, request, send_file, url_for

app = Flask(__name__)
DATABASE = "polls.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS polls (
                id TEXT PRIMARY KEY,
                question TEXT NOT NULL
            )
        """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS options (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                poll_id TEXT NOT NULL,
                text TEXT NOT NULL,
                votes INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (poll_id) REFERENCES polls(id)
            )
        """
        )
        conn.commit()


@app.route("/")
def index():
    with get_db() as conn:
        polls = conn.execute("SELECT * FROM polls").fetchall()
    return render_template("index.html", polls=polls)


@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        question = request.form.get("question", "").strip()
        options = [
            opt.strip()
            for opt in request.form.getlist("options")
            if opt.strip()
        ]
        if question and len(options) >= 2:
            poll_id = uuid.uuid4().hex
            with get_db() as conn:
                conn.execute(
                    "INSERT INTO polls (id, question) VALUES (?, ?)",
                    (poll_id, question),
                )
                for option in options:
                    conn.execute(
                        "INSERT INTO options (poll_id, text) VALUES (?, ?)",
                        (poll_id, option),
                    )
                conn.commit()
            return redirect(url_for("poll", poll_id=poll_id))
    return render_template("create.html")


@app.route("/poll/<poll_id>", methods=["GET", "POST"])
def poll(poll_id):
    with get_db() as conn:
        poll_row = conn.execute(
            "SELECT * FROM polls WHERE id = ?", (poll_id,)
        ).fetchone()
        if poll_row is None:
            return "Poll not found", 404
        options = conn.execute(
            "SELECT * FROM options WHERE poll_id = ?", (poll_id,)
        ).fetchall()

        if request.method == "POST":
            option_id = request.form.get("option_id")
            if option_id:
                conn.execute(
                    "UPDATE options SET votes = votes + 1 WHERE id = ? AND poll_id = ?",
                    (option_id, poll_id),
                )
                conn.commit()
            return redirect(url_for("results", poll_id=poll_id))

    return render_template("poll.html", poll=poll_row, options=options)


@app.route("/results/<poll_id>")
def results(poll_id):
    with get_db() as conn:
        poll_row = conn.execute(
            "SELECT * FROM polls WHERE id = ?", (poll_id,)
        ).fetchone()
        if poll_row is None:
            return "Poll not found", 404
        options = conn.execute(
            "SELECT * FROM options WHERE poll_id = ?", (poll_id,)
        ).fetchall()
    total_votes = sum(opt["votes"] for opt in options)
    return render_template(
        "results.html", poll=poll_row, options=options, total_votes=total_votes
    )


@app.route("/qr/<poll_id>")
def qr_code(poll_id):
    url = url_for("poll", poll_id=poll_id, _external=True)
    img = qrcode.make(url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")


init_db()

if __name__ == "__main__":
    app.run(debug=True)
