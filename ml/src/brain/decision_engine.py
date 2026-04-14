import re
import logging
from typing import Dict, Any

logger = logging.getLogger("DecisionEngine")

class DecisionEngine:
    """
    Evaluates user responses to dynamically route the interview flow.
    Decides between LLM_DRILL_DOWN (follow-up questions) and 
    RAG_NEW_TOPIC (moving to a structural new topic).
    Also adjusts interview difficulty based on rolling performance proxies.
    """
    
    ACTION_LLM_DRILL_DOWN = "LLM_DRILL_DOWN"
    ACTION_RAG_NEW_TOPIC = "RAG_NEW_TOPIC"

    def __init__(self):
        # Tracking recent decisions to avoid getting stuck in drill-downs forever
        self.drill_down_count = 0
        self.MAX_CONSECUTIVE_DRILL_DOWNS = 2

        # Difficulty tracking ranges from 1 to 5 (1=Easy, 3=Medium, 5=Hard)
        self.current_difficulty_score = 3
        
        # Phrases indicating the user is giving up or completely lost
        self.hesitation_phrases = [
            "i don't know", "i do not know", "i am not sure", "i'm not sure",
            "not sure", "no idea", "pass", "next question", "skip",
            "i can't remember", "forgot", "no clue"
        ]

    def evaluate(self, user_text: str, current_difficulty: str) -> Dict[str, Any]:
        """
        Evaluate the latest answer to determine next action.
        Returns a dict with 'action', 'new_difficulty', and logical reasons.
        """
        text = user_text.lower().strip()
        word_count = len(text.split())

        # 1. Check for explicit hesitation / giving up
        if any(phrase in text for phrase in self.hesitation_phrases) and word_count < 15:
            logger.info("DecisionEngine: Detected hesitation/skip. Routing to RAG.")
            self._adjust_difficulty(-1)
            self.drill_down_count = 0
            return self._build_result(self.ACTION_RAG_NEW_TOPIC, current_difficulty, "User hesitated or asked to skip.")

        # 2. Check for extremely short answers (weak signal)
        if word_count < 8:
            logger.info("DecisionEngine: Answer too short for drill-down. Routing to RAG.")
            self._adjust_difficulty(-0.5)
            self.drill_down_count = 0
            return self._build_result(self.ACTION_RAG_NEW_TOPIC, current_difficulty, "Answer too brief.")

        # 3. Check drill-down saturation
        if self.drill_down_count >= self.MAX_CONSECUTIVE_DRILL_DOWNS:
            logger.info("DecisionEngine: Reached max drill-downs. Forcing new topic via RAG.")
            self.drill_down_count = 0
            # User survived a deep drill-down! Increase difficulty
            self._adjust_difficulty(1)
            return self._build_result(self.ACTION_RAG_NEW_TOPIC, current_difficulty, "Max consecutive drill-downs reached.")

        # 4. Detailed answer -> LLM Drill Down
        logger.info("DecisionEngine: Good answer detected. Routing to LLM for drill-down.")
        self.drill_down_count += 1
        self._adjust_difficulty(0.5)
        return self._build_result(self.ACTION_LLM_DRILL_DOWN, current_difficulty, "Detailed answer requires follow-up.")

    def _adjust_difficulty(self, diff_delta: float):
        """Clamp difficulty between 1 and 5."""
        self.current_difficulty_score = max(1, min(5, self.current_difficulty_score + diff_delta))

    def _build_result(self, action: str, old_diff_str: str, reason: str) -> Dict[str, Any]:
        """Maps internal difficulty score back to Easy/Medium/Hard string."""
        new_diff_str = "Medium"
        if self.current_difficulty_score <= 2:
            new_diff_str = "Easy"
        elif self.current_difficulty_score >= 4:
            new_diff_str = "Hard"

        if old_diff_str != new_diff_str:
            logger.info(f"DecisionEngine: Difficulty scaling from {old_diff_str} to {new_diff_str}!")

        return {
            "action": action,
            "new_difficulty": new_diff_str,
            "reason": reason
        }
