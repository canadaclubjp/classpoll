import io
import functools
import qrcode
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    abort,
    current_app,
    send_file,
    flash,
)
from . import db
from .models import Poll, Question, Choice, Submission, Answer

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def require_admin(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        token = kwargs.pop("token", None)
        if token != current_app.config["ADMIN_TOKEN"]:
            abort(403)
        return f(*args, token=token, **kwargs)

    return decorated


# ── Dashboard ─────────────────────────────────────────────────────────────────

@admin_bp.route("/<token>")
@require_admin
def dashboard(token):
    polls = Poll.query.order_by(Poll.created_at.desc()).all()
    return render_template("admin/dashboard.html", polls=polls, token=token)


# ── Create poll ───────────────────────────────────────────────────────────────

@admin_bp.route("/<token>/create", methods=["GET", "POST"])
@require_admin
def create_poll(token):
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        if not title:
            flash("Poll title is required.", "error")
            return redirect(url_for("admin.create_poll", token=token))

        question_texts = request.form.getlist("question_text[]")
        question_types = request.form.getlist("question_type[]")
        # choices are passed as nested: choices_0[], choices_1[], …
        num_questions = len(question_texts)

        if num_questions < 2 or num_questions > 5:
            flash("A poll must have between 2 and 5 questions.", "error")
            return redirect(url_for("admin.create_poll", token=token))

        poll = Poll.create(title)
        db.session.add(poll)
        db.session.flush()  # get poll.id

        for i, (qtext, qtype) in enumerate(zip(question_texts, question_types)):
            qtext = qtext.strip()
            if not qtext:
                flash(f"Question {i + 1} text is required.", "error")
                db.session.rollback()
                return redirect(url_for("admin.create_poll", token=token))
            if qtype not in ("mc", "text"):
                abort(400)

            required = qtype == "mc"
            question = Question(
                poll_id=poll.id,
                position=i,
                text=qtext,
                qtype=qtype,
                required=required,
            )
            db.session.add(question)
            db.session.flush()

            if qtype == "mc":
                choices_raw = request.form.getlist(f"choices_{i}[]")
                choices = [c.strip() for c in choices_raw if c.strip()]
                if len(choices) < 2:
                    flash(f"Question {i + 1}: multiple-choice needs at least 2 options.", "error")
                    db.session.rollback()
                    return redirect(url_for("admin.create_poll", token=token))
                for j, ctext in enumerate(choices):
                    db.session.add(Choice(question_id=question.id, position=j, text=ctext))

        db.session.commit()
        flash("Poll created.", "success")
        return redirect(url_for("admin.poll_detail", token=token, public_id=poll.public_id))

    return render_template("admin/create_poll.html", token=token)


# ── Poll detail ───────────────────────────────────────────────────────────────

@admin_bp.route("/<token>/poll/<public_id>")
@require_admin
def poll_detail(token, public_id):
    poll = Poll.query.filter_by(public_id=public_id).first_or_404()
    student_url = url_for("student.poll_view", public_id=public_id, _external=True)
    return render_template(
        "admin/poll_detail.html",
        poll=poll,
        token=token,
        student_url=student_url,
    )


# ── Open / Close ──────────────────────────────────────────────────────────────

@admin_bp.route("/<token>/poll/<public_id>/open", methods=["POST"])
@require_admin
def open_poll(token, public_id):
    poll = Poll.query.filter_by(public_id=public_id).first_or_404()
    poll.is_open = True
    db.session.commit()
    flash("Poll is now open.", "success")
    return redirect(url_for("admin.poll_detail", token=token, public_id=public_id))


@admin_bp.route("/<token>/poll/<public_id>/close", methods=["POST"])
@require_admin
def close_poll(token, public_id):
    poll = Poll.query.filter_by(public_id=public_id).first_or_404()
    poll.is_open = False
    db.session.commit()
    flash("Poll is now closed.", "success")
    return redirect(url_for("admin.poll_detail", token=token, public_id=public_id))


# ── Delete ────────────────────────────────────────────────────────────────────

@admin_bp.route("/<token>/poll/<public_id>/delete", methods=["POST"])
@require_admin
def delete_poll(token, public_id):
    poll = Poll.query.filter_by(public_id=public_id).first_or_404()
    db.session.delete(poll)
    db.session.commit()
    flash("Poll deleted.", "success")
    return redirect(url_for("admin.dashboard", token=token))


# ── Results ───────────────────────────────────────────────────────────────────

@admin_bp.route("/<token>/poll/<public_id>/results")
@require_admin
def poll_results(token, public_id):
    poll = Poll.query.filter_by(public_id=public_id).first_or_404()
    total_submissions = Submission.query.filter_by(poll_id=poll.id).count()

    results = []
    for question in poll.questions:
        if question.qtype == "mc":
            choice_counts = {}
            for choice in question.choices:
                count = Answer.query.filter_by(
                    question_id=question.id, choice_id=choice.id
                ).count()
                pct = round(count / total_submissions * 100, 1) if total_submissions else 0
                choice_counts[choice.id] = {"text": choice.text, "count": count, "pct": pct}
            results.append({"question": question, "type": "mc", "choice_counts": choice_counts})
        else:
            text_answers = (
                Answer.query.filter_by(question_id=question.id)
                .filter(Answer.text_value.isnot(None))
                .all()
            )
            results.append({"question": question, "type": "text", "texts": [a.text_value for a in text_answers]})

    return render_template(
        "admin/results.html",
        poll=poll,
        token=token,
        results=results,
        total_submissions=total_submissions,
    )


# ── QR code ───────────────────────────────────────────────────────────────────

@admin_bp.route("/<token>/poll/<public_id>/qr.png")
@require_admin
def poll_qr(token, public_id):
    poll = Poll.query.filter_by(public_id=public_id).first_or_404()
    student_url = url_for("student.poll_view", public_id=public_id, _external=True)

    img = qrcode.make(student_url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")
