"""
poll.py – Data models and SQLite-backed persistence for classpoll.

Each Poll has an id, a question, a list of options, and a vote tally.
Poll data is saved to a local SQLite database (classpoll.db) so polls
survive server restarts.
"""

import json
import os
import sqlite3
import uuid
from dataclasses import dataclass, field
from typing import Dict, List

# Path to the SQLite database file (same directory as this module).
DB_PATH = os.path.join(os.path.dirname(__file__), "classpoll.db")


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db() -> None:
    """Create the polls table if it does not exist yet."""
    with _get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS polls (
                id       TEXT PRIMARY KEY,
                question TEXT NOT NULL,
                options  TEXT NOT NULL,
                votes    TEXT NOT NULL,
                is_open  INTEGER NOT NULL DEFAULT 1
            )
            """
        )


# Initialise on import.
_init_db()


@dataclass
class Poll:
    """Represents a single classroom poll."""

    question: str
    options: List[str]
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    votes: Dict[str, int] = field(default_factory=dict)
    open: bool = True

    def __post_init__(self):
        # Initialise every option with zero votes.
        for option in self.options:
            if option not in self.votes:
                self.votes[option] = 0

    def cast_vote(self, option: str) -> bool:
        """Record one vote for *option*.  Returns True on success."""
        if not self.open:
            return False
        if option not in self.votes:
            return False
        self.votes[option] += 1
        save_poll(self)
        return True

    def total_votes(self) -> int:
        return sum(self.votes.values())

    def percentage(self, option: str) -> float:
        total = self.total_votes()
        if total == 0:
            return 0.0
        return round(self.votes.get(option, 0) / total * 100, 1)

    def close(self):
        self.open = False
        save_poll(self)

    def reopen(self):
        self.open = True
        save_poll(self)

    def reset(self):
        for option in self.options:
            self.votes[option] = 0
        save_poll(self)


# ---------------------------------------------------------------------------
# SQLite-backed persistence helpers.
# ---------------------------------------------------------------------------

def _row_to_poll(row: sqlite3.Row) -> Poll:
    return Poll(
        id=row["id"],
        question=row["question"],
        options=json.loads(row["options"]),
        votes=json.loads(row["votes"]),
        open=bool(row["is_open"]),
    )


def save_poll(poll: "Poll") -> None:
    """Insert or update a poll in the database."""
    with _get_conn() as conn:
        conn.execute(
            """
            INSERT INTO polls (id, question, options, votes, is_open)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                question = excluded.question,
                options  = excluded.options,
                votes    = excluded.votes,
                is_open  = excluded.is_open
            """,
            (
                poll.id,
                poll.question,
                json.dumps(poll.options),
                json.dumps(poll.votes),
                int(poll.open),
            ),
        )


def create_poll(question: str, options: List[str]) -> Poll:
    """Create a new poll and persist it to the database."""
    if len(options) < 2:
        raise ValueError("A poll must have at least two options.")
    cleaned = [o.strip() for o in options if o.strip()]
    if len(cleaned) < 2:
        raise ValueError("A poll must have at least two non-empty options.")
    poll = Poll(question=question.strip(), options=cleaned)
    save_poll(poll)
    return poll


def get_poll(poll_id: str) -> "Poll | None":
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM polls WHERE id = ?", (poll_id,)
        ).fetchone()
    return _row_to_poll(row) if row else None


def all_polls() -> List[Poll]:
    with _get_conn() as conn:
        rows = conn.execute("SELECT * FROM polls").fetchall()
    return [_row_to_poll(r) for r in rows]


def delete_poll(poll_id: str) -> bool:
    with _get_conn() as conn:
        cursor = conn.execute("DELETE FROM polls WHERE id = ?", (poll_id,))
    return cursor.rowcount > 0
