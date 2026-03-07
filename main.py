"""
main.py – Classpoll Flask application.

Run with:
    python main.py

Then open http://127.0.0.1:5000 in your browser.

Set the SECRET_KEY environment variable before running in production:
    export SECRET_KEY="your-random-secret-here"
"""

import os

from flask import Flask, redirect, render_template, request, url_for, flash

import poll as poll_module

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "classpoll-dev-secret-change-me")


# ---------------------------------------------------------------------------
# Home – list all polls
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html", polls=poll_module.all_polls())


# ---------------------------------------------------------------------------
# Create a new poll
# ---------------------------------------------------------------------------
@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        question = request.form.get("question", "").strip()
        # Collect up to 6 options from the form.
        options = [
            request.form.get(f"option{i}", "").strip() for i in range(1, 7)
        ]
        options = [o for o in options if o]  # drop empty entries

        if not question:
            flash("Please enter a question.", "error")
            return render_template("create.html")

        if len(options) < 2:
            flash("Please enter at least two options.", "error")
            return render_template("create.html")

        new_poll = poll_module.create_poll(question, options)
        flash("Poll created!", "success")
        return redirect(url_for("vote", poll_id=new_poll.id))

    return render_template("create.html")


# ---------------------------------------------------------------------------
# Vote on a poll
# ---------------------------------------------------------------------------
@app.route("/poll/<poll_id>", methods=["GET", "POST"])
def vote(poll_id):
    p = poll_module.get_poll(poll_id)
    if p is None:
        flash("Poll not found.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        chosen = request.form.get("option")
        if not chosen:
            flash("Please select an option before voting.", "error")
            return render_template("poll.html", poll=p)

        if p.cast_vote(chosen):
            flash("Your vote has been recorded!", "success")
            return redirect(url_for("results", poll_id=poll_id))
        else:
            flash("This poll is closed.", "error")

    return render_template("poll.html", poll=p)


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------
@app.route("/results/<poll_id>")
def results(poll_id):
    p = poll_module.get_poll(poll_id)
    if p is None:
        flash("Poll not found.", "error")
        return redirect(url_for("index"))
    return render_template("results.html", poll=p)


# ---------------------------------------------------------------------------
# Admin actions: close, reopen, reset, delete
# ---------------------------------------------------------------------------
@app.route("/close/<poll_id>", methods=["POST"])
def close_poll(poll_id):
    p = poll_module.get_poll(poll_id)
    if p:
        p.close()
        flash("Poll closed.", "success")
    return redirect(url_for("results", poll_id=poll_id))


@app.route("/reopen/<poll_id>", methods=["POST"])
def reopen_poll(poll_id):
    p = poll_module.get_poll(poll_id)
    if p:
        p.reopen()
        flash("Poll reopened.", "success")
    return redirect(url_for("results", poll_id=poll_id))


@app.route("/reset/<poll_id>", methods=["POST"])
def reset_poll(poll_id):
    p = poll_module.get_poll(poll_id)
    if p:
        p.reset()
        flash("Votes have been reset.", "success")
    return redirect(url_for("results", poll_id=poll_id))


@app.route("/delete/<poll_id>", methods=["POST"])
def delete_poll(poll_id):
    poll_module.delete_poll(poll_id)
    flash("Poll deleted.", "success")
    return redirect(url_for("index"))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug)
