from datetime import datetime, timezone, timedelta
import uuid
from . import db


class Poll(db.Model):
    __tablename__ = "polls"

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(
        db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4())
    )
    title = db.Column(db.String(200), nullable=False)
    is_open = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)

    questions = db.relationship(
        "Question", back_populates="poll", cascade="all, delete-orphan", order_by="Question.position"
    )
    submissions = db.relationship(
        "Submission", back_populates="poll", cascade="all, delete-orphan"
    )

    def is_expired(self):
        now = datetime.now(timezone.utc)
        expires = self.expires_at
        # SQLite stores naive datetimes; treat them as UTC
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        return now >= expires

    @staticmethod
    def create(title):
        now = datetime.now(timezone.utc)
        return Poll(
            title=title,
            expires_at=now + timedelta(hours=24),
        )


class Question(db.Model):
    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, db.ForeignKey("polls.id"), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    text = db.Column(db.String(500), nullable=False)
    # "mc" = multiple choice, "text" = short text
    qtype = db.Column(db.String(10), nullable=False)
    required = db.Column(db.Boolean, default=True, nullable=False)

    poll = db.relationship("Poll", back_populates="questions")
    choices = db.relationship(
        "Choice", back_populates="question", cascade="all, delete-orphan", order_by="Choice.position"
    )
    answers = db.relationship(
        "Answer", back_populates="question", cascade="all, delete-orphan"
    )


class Choice(db.Model):
    __tablename__ = "choices"

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    text = db.Column(db.String(300), nullable=False)

    question = db.relationship("Question", back_populates="choices")
    answers = db.relationship(
        "Answer", back_populates="choice", cascade="all, delete-orphan"
    )


class Submission(db.Model):
    __tablename__ = "submissions"

    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, db.ForeignKey("polls.id"), nullable=False)
    attempt_id = db.Column(db.String(36), nullable=False)
    submitted_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        db.UniqueConstraint("poll_id", "attempt_id", name="uq_submission_poll_attempt"),
    )

    poll = db.relationship("Poll", back_populates="submissions")
    answers = db.relationship(
        "Answer", back_populates="submission", cascade="all, delete-orphan"
    )


class Answer(db.Model):
    __tablename__ = "answers"

    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(
        db.Integer, db.ForeignKey("submissions.id"), nullable=False
    )
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    # For MC: store choice_id; for text: store text_value
    choice_id = db.Column(db.Integer, db.ForeignKey("choices.id"), nullable=True)
    text_value = db.Column(db.String(1000), nullable=True)

    submission = db.relationship("Submission", back_populates="answers")
    question = db.relationship("Question", back_populates="answers")
    choice = db.relationship("Choice", back_populates="answers")
