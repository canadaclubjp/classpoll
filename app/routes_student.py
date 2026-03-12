import uuid
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    make_response,
    abort,
    flash,
)
from .extensions import db
from .models import Poll, Submission, Answer

student_bp = Blueprint("student", __name__)

COOKIE_MAX_AGE = 60 * 60 * 24 * 2  # 2 days


@student_bp.route("/")
def index():
    return render_template("landing.html")


def _get_or_create_attempt(poll_public_id):
    """Return (attempt_id, is_new). Sets cookie on response when new."""
    cookie_name = f"attempt_{poll_public_id}"
    attempt_id = request.cookies.get(cookie_name)
    is_new = attempt_id is None
    if is_new:
        attempt_id = str(uuid.uuid4())
    return attempt_id, is_new, cookie_name


@student_bp.route("/poll/<public_id>", methods=["GET"])
def poll_view(public_id):
    poll = Poll.query.filter_by(public_id=public_id).first_or_404()

    if poll.is_expired():
        return render_template("student/expired.html", poll=poll), 410

    attempt_id, is_new, cookie_name = _get_or_create_attempt(public_id)

    # Find prior submission if any
    prior = None
    prior_answers = {}
    if not is_new:
        prior = Submission.query.filter_by(
            poll_id=poll.id, attempt_id=attempt_id
        ).first()
        if prior:
            for ans in prior.answers:
                if ans.choice_id is not None:
                    prior_answers[ans.question_id] = ans.choice_id
                else:
                    prior_answers[ans.question_id] = ans.text_value

    resp = make_response(
        render_template(
            "student/poll.html",
            poll=poll,
            prior_answers=prior_answers,
            already_submitted=prior is not None,
        )
    )
    if is_new:
        resp.set_cookie(cookie_name, attempt_id, max_age=COOKIE_MAX_AGE, httponly=True, samesite="Lax")
    return resp


@student_bp.route("/poll/<public_id>/submit", methods=["POST"])
def poll_submit(public_id):
    poll = Poll.query.filter_by(public_id=public_id).first_or_404()

    if poll.is_expired():
        abort(410)

    if not poll.is_open:
        abort(403)

    attempt_id, is_new, cookie_name = _get_or_create_attempt(public_id)

    # Delete prior submission if exists (overwrite)
    prior = Submission.query.filter_by(
        poll_id=poll.id, attempt_id=attempt_id
    ).first()
    if prior:
        db.session.delete(prior)
        db.session.flush()

    # Validate and collect answers
    answers = []
    for question in poll.questions:
        field_name = f"q_{question.id}"
        if question.qtype == "mc":
            choice_id_str = request.form.get(field_name)
            if not choice_id_str:
                flash(f'Question "{question.text}" is required.', "error")
                return redirect(url_for("student.poll_view", public_id=public_id))
            choice_id = int(choice_id_str)
            # Validate choice belongs to question
            valid_ids = [c.id for c in question.choices]
            if choice_id not in valid_ids:
                abort(400)
            answers.append(Answer(question_id=question.id, choice_id=choice_id))
        else:  # text
            text_val = request.form.get(field_name, "").strip()
            answers.append(Answer(question_id=question.id, text_value=text_val or None))

    submission = Submission(poll_id=poll.id, attempt_id=attempt_id, answers=answers)
    db.session.add(submission)
    db.session.commit()

    resp = make_response(
        render_template("student/submitted.html", poll=poll)
    )
    if is_new:
        resp.set_cookie(cookie_name, attempt_id, max_age=COOKIE_MAX_AGE, httponly=True, samesite="Lax")
    return resp
