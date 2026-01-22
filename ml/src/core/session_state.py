from dataclasses import dataclass, field
import time

@dataclass
class SessionState:
    session_id: str = field(default_factory=lambda: str(int(time.time())))
    difficulty: str = "Medium"
    question_count: int = 0
    is_active: bool = True
    
    def update_difficulty(self, new_diff):
        if new_diff in ["Easy", "Medium", "Hard", "Extreme"]:
            self.difficulty = new_diff