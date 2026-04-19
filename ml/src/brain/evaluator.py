import json
import logging
from pathlib import Path

from config import settings

logger = logging.getLogger("Evaluator")

MAX_EVAL_TOKENS = 800
EVAL_TEMPERATURE = 0.1


class Evaluator:
    """Generates post-interview evaluation reports using the LLM (Ollama)."""

    def __init__(self, model_path: str | Path = None, llm_model: Llama | None = None) -> None:
        self.model_path = model_path
        self.llm = None
    
    def _ensure_llm_loaded(self) -> None:
        if self.llm is None:
            from src.brain.llm_engine import OllamaClient
            self.llm = OllamaClient()

    def generate_report(self, history: list[dict],
                        per_question_scores: list[dict] | None = None) -> dict:
        """Generate a structured evaluation report from interview history.

        Args:
            history: Full conversation history.
            per_question_scores: Optional per-question evaluations from QuestionEvaluator.
        """
        logger.info("Generating Final Evaluation Report...")

        if len(history) < 1:
            return {
                "score": 0,
                "mistakes": ["Interview was terminated too early."],
                "suggestions": ["Please complete a full session for analysis."],
                "domain_rating": {"hr": -1, "technical": -1, "communication": -1},
                "swot_analysis": {
                    "strengths": ["Insufficient data"],
                    "weaknesses": ["Interview incomplete"],
                    "opportunities": ["Complete full interview for detailed analysis"],
                    "threats": ["Unable to assess"]
                }
            }

        self._ensure_llm_loaded()

        prompt = (
            "You are a strict Senior Technical Hiring Manager. Analyze the interview transcript below.\n"
            "RULES:\n"
            "1. If a topic (HR, Technical, Communication) was NOT discussed, set its rating to -1.\n"
            "2. If the candidate gave short, lazy, or refusal answers (e.g., 'I am not ready'), score them 0.\n"
            "3. Do not hallucinate. Only evaluate what is explicitly in the text.\n"
            "4. Output strictly valid JSON.\n\n"
            "Transcript:\n" + json.dumps(history) + "\n\n"
            "Output Format:\n"
            "{\n"
            '  "score": (int 0-100, be harsh),\n'
            '  "mistakes": [list of specific errors],\n'
            '  "suggestions": [list of actionable advice],\n'
            '  "domain_rating": {"hr": int, "technical": int, "communication": int},\n'
            '  "swot_analysis": {\n'
            '    "strengths": [list of 3-5 key strengths],\n'
            '    "weaknesses": [list of 3-5 weaknesses],\n'
            '    "opportunities": [list of 3-5 growth opportunities],\n'
            '    "threats": [list of 3-5 potential concerns]\n'
            '  }\n'
            "}"
        )

        try:
            output = self.llm.create_chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=MAX_EVAL_TOKENS,
                temperature=EVAL_TEMPERATURE,
                response_format={"type": "json_object"},
                num_ctx=4096,  # Evaluator needs more context for full transcript
            )
            report = json.loads(output['choices'][0]['message']['content'])

            # Attach per-question scores if available
            if per_question_scores:
                report["per_question_evaluations"] = per_question_scores

                # Aggregate per-question metrics
                from src.brain.question_evaluator import QuestionEvaluator
                aggregator = QuestionEvaluator()
                report["question_bank_summary"] = aggregator.aggregate_scores(per_question_scores)

            return report

        except Exception as e:
            logger.error(f"Failed to generate evaluation: {e}", exc_info=True)
            return {
                "error": "LLM returned invalid JSON payload",
                "details": str(e),
                "raw": raw_content if 'raw_content' in locals() else None,
                "score": 0,
                "mistakes": ["Evaluation system parsing error"],
                "suggestions": ["Please review transcripts manually"],
                "domain_rating": {"hr": 0, "technical": 0, "communication": 0},
                "swot_analysis": {
                    "strengths": ["N/A"], "weaknesses": ["N/A"],
                    "opportunities": ["N/A"], "threats": ["N/A"]
                }
            }