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
from .extensions import db
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
        question_text = request.form.get("question", "").strip()
        options = [o.strip() for o in request.form.getlist("options[]") if o.strip()]

        if not question_text:
            flash("Question is required.", "error")
            return redirect(url_for("admin.create_poll", token=token))
        if len(options) < 2:
            flash("At least 2 options are required.", "error")
            return redirect(url_for("admin.create_poll", token=token))

        poll = Poll.create(question_text)
        db.session.add(poll)
        db.session.flush()

        question = Question(
            poll_id=poll.id, position=0, text=question_text, qtype="mc", required=True
        )
        db.session.add(question)
        db.session.flush()

        for j, ctext in enumerate(options):
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

    total_votes = Submission.query.filter_by(poll_id=poll.id).count()
    question = next((q for q in poll.questions if q.qtype == "mc"), None)
    options = []
    if question:
        for choice in question.choices:
            count = Answer.query.filter_by(
                question_id=question.id, choice_id=choice.id
            ).count()
            pct = (count / total_votes * 100) if total_votes else 0
            options.append({"text": choice.text, "votes": count, "pct": pct})

    return render_template(
        "admin/poll_detail.html",
        poll=poll,
        token=token,
        student_url=student_url,
        total_votes=total_votes,
        options=options,
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


# ── Reset votes ───────────────────────────────────────────────────────────────

@admin_bp.route("/<token>/poll/<public_id>/reset", methods=["POST"])
@require_admin
def reset_votes(token, public_id):
    poll = Poll.query.filter_by(public_id=public_id).first_or_404()
    for submission in Submission.query.filter_by(poll_id=poll.id).all():
        db.session.delete(submission)
    db.session.commit()
    flash("Votes reset.", "success")
    return redirect(url_for("admin.poll_detail", token=token, public_id=public_id))


# ── Results (redirects to poll detail which now shows results inline) ─────────

@admin_bp.route("/<token>/poll/<public_id>/results")
@require_admin
def poll_results(token, public_id):
    return redirect(url_for("admin.poll_detail", token=token, public_id=public_id))


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
