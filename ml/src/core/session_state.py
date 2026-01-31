from dataclasses import dataclass, field
import time
import secrets

@dataclass
class SessionState:
    session_id: str = field(default_factory=lambda: secrets.token_hex(16))
    difficulty: str = "Medium"
    question_count: int = 0
    is_active: bool = True
    
    def update_difficulty(self, new_diff):
        if new_diff in ["Easy", "Medium", "Hard", "Extreme"]:
            self.difficulty = new_diff