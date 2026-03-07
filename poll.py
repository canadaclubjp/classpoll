"""
poll.py – Data models for classpoll.

Polls are kept in memory while the server is running.
Each Poll has an id, a question, a list of options, and a vote tally.
"""

import uuid
from dataclasses import dataclass, field
from typing import Dict, List


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

    def reopen(self):
        self.open = True

    def reset(self):
        for option in self.options:
            self.votes[option] = 0


# ---------------------------------------------------------------------------
# In-memory store shared across the whole application.
# ---------------------------------------------------------------------------
polls: Dict[str, Poll] = {}


def create_poll(question: str, options: List[str]) -> Poll:
    """Create a new poll and add it to the store."""
    if len(options) < 2:
        raise ValueError("A poll must have at least two options.")
    cleaned = [o.strip() for o in options if o.strip()]
    if len(cleaned) < 2:
        raise ValueError("A poll must have at least two non-empty options.")
    poll = Poll(question=question.strip(), options=cleaned)
    polls[poll.id] = poll
    return poll


def get_poll(poll_id: str) -> Poll | None:
    return polls.get(poll_id)


def all_polls() -> List[Poll]:
    return list(polls.values())


def delete_poll(poll_id: str) -> bool:
    if poll_id in polls:
        del polls[poll_id]
        return True
    return False
