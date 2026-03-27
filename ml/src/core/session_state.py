import secrets
import time
from dataclasses import dataclass, field

VALID_DIFFICULTIES = ("Easy", "Medium", "Hard", "Extreme")
VALID_MODES = ("generic", "curated")
VALID_INTERVIEW_TYPES = ("technical", "behavioral", "hr", "combined")


@dataclass
class SessionState:
    """Tracks interview session metadata and state."""

    session_id: str = field(default_factory=lambda: secrets.token_hex(16))
    difficulty: str = "Medium"
    interview_mode: str = "generic"
    interview_type: str = "technical"
    question_count: int = 0
    is_active: bool = True
    started_at: float = field(default_factory=time.time)

    def update_difficulty(self, new_diff: str) -> bool:
        """Update difficulty if valid. Returns True on success."""
        if new_diff not in VALID_DIFFICULTIES:
            return False
        self.difficulty = new_diff
        return True

    def update_mode(self, mode: str) -> bool:
        """Update interview mode if valid. Returns True on success."""
        if mode not in VALID_MODES:
            return False
        self.interview_mode = mode
        return True

    def update_interview_type(self, itype: str) -> bool:
        """Update interview type if valid. Returns True on success."""
        if itype not in VALID_INTERVIEW_TYPES:
            return False
        self.interview_type = itype
        return True

    def increment_question(self) -> int:
        """Increment and return the new question count."""
        self.question_count += 1
        return self.question_count

    def elapsed_seconds(self) -> float:
        """Return seconds since session started."""
        return time.time() - self.started_at

    def to_dict(self) -> dict:
        """Serialize state for JSON storage."""
        return {
            "session_id": self.session_id,
            "difficulty": self.difficulty,
            "interview_mode": self.interview_mode,
            "interview_type": self.interview_type,
            "question_count": self.question_count,
            "is_active": self.is_active,
            "started_at": self.started_at,
            "elapsed_seconds": round(self.elapsed_seconds(), 1),
        }

    def __repr__(self) -> str:
        return (
            f"SessionState(id={self.session_id[:8]}..., "
            f"mode={self.interview_mode}, "
            f"type={self.interview_type}, "
            f"difficulty={self.difficulty}, "
            f"questions={self.question_count}, "
            f"active={self.is_active})"
        )