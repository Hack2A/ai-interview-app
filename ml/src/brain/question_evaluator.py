"""Per-question answer evaluator — scores individual candidate answers
against ideal answers with structured feedback.
"""
from __future__ import annotations

import json
import logging
from typing import Optional

from config import settings

logger = logging.getLogger("QuestionEvaluator")


EVALUATION_PROMPT_TEMPLATE = """You are a strict Senior Technical Interviewer evaluating a candidate's answer.

INTERVIEW QUESTION:
{question}

IDEAL/REFERENCE ANSWER:
{ideal_answer}

EVALUATION CRITERIA:
{evaluation_points}

CANDIDATE'S ANSWER:
{candidate_answer}

RULES:
1. Be harsh but fair. Compare the candidate's answer against the ideal answer.
2. If the candidate gave a lazy, off-topic, or refusal answer, score them 0-2.
3. If the answer is partially correct but missing depth, score 4-6.
4. Only score 8-10 if the answer demonstrates strong understanding AND communication.
5. Output strictly valid JSON.

Output this exact JSON format:
{{
  "score": <float 0-10>,
  "technical_accuracy": <int 0-10>,
  "clarity": <int 0-10>,
  "communication": <int 0-10>,
  "strengths": ["list of 1-3 specific things done well"],
  "weaknesses": ["list of 1-3 specific gaps or errors"],
  "suggested_improvement": "one sentence of actionable advice"
}}"""


FOLLOW_UP_PROMPT_TEMPLATE = """You are a senior technical interviewer. Based on the candidate's answer quality, generate ONE follow-up question.

ORIGINAL QUESTION: {question}
CANDIDATE'S ANSWER: {candidate_answer}
SCORE: {score}/10

RULES:
- If score >= 7: Ask a HARDER follow-up that goes deeper into the topic.
- If score 4-6: Ask a clarifying question about the weakest part of their answer.
- If score < 4: Ask a simpler, more fundamental version of the same topic.
- Keep the follow-up to ONE clear question.
- Do NOT lecture or explain — just ask the question.

Follow-up question:"""


class QuestionEvaluator:
    """Evaluates individual candidate answers against ideal answers."""

    def __init__(self) -> None:
        self.weights = {
            "technical_accuracy": settings.SCORING_WEIGHT_TECHNICAL,
            "clarity": settings.SCORING_WEIGHT_CLARITY,
            "communication": settings.SCORING_WEIGHT_COMMUNICATION,
        }

    def evaluate_answer(
        self,
        question: str,
        candidate_answer: str,
        ideal_answer: str,
        evaluation_points: list[str],
        llm_model,
    ) -> dict:
        """Evaluate a single answer against the ideal.

        Returns structured feedback with scores and actionable advice.
        """
        if not candidate_answer or len(candidate_answer.strip()) < 5:
            return self._empty_response("No meaningful answer provided")

        prompt = EVALUATION_PROMPT_TEMPLATE.format(
            question=question,
            ideal_answer=ideal_answer or "No reference answer available — evaluate based on general knowledge.",
            evaluation_points=", ".join(evaluation_points) if evaluation_points else "technical accuracy, clarity, depth",
            candidate_answer=candidate_answer,
        )

        try:
            output = llm_model.create_chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.1,
                response_format={"type": "json_object"},
            )

            result = json.loads(output["choices"][0]["message"]["content"])

            # Calculate weighted score
            weighted = (
                result.get("technical_accuracy", 5) * self.weights["technical_accuracy"]
                + result.get("clarity", 5) * self.weights["clarity"]
                + result.get("communication", 5) * self.weights["communication"]
            )
            result["weighted_score"] = round(weighted, 1)

            return result

        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            return self._empty_response(f"Evaluation error: {str(e)}")

    def generate_follow_up(
        self,
        question: str,
        candidate_answer: str,
        score: float,
        llm_model,
    ) -> str:
        """Generate a contextual follow-up question based on answer quality."""
        prompt = FOLLOW_UP_PROMPT_TEMPLATE.format(
            question=question,
            candidate_answer=candidate_answer,
            score=score,
        )

        try:
            output = llm_model.create_chat_completion(
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.5,
            )
            return output["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.warning(f"Follow-up generation failed: {e}")
            return ""

    def aggregate_scores(self, per_question_scores: list[dict]) -> dict:
        """Aggregate all per-question scores into a session summary."""
        if not per_question_scores:
            return {
                "overall_score": 0,
                "avg_technical": 0,
                "avg_clarity": 0,
                "avg_communication": 0,
                "total_questions": 0,
                "all_strengths": [],
                "all_weaknesses": [],
            }

        valid = [s for s in per_question_scores if "technical_accuracy" in s]
        if not valid:
            return {
                "overall_score": 0,
                "total_questions": len(per_question_scores),
                "note": "No valid evaluations to aggregate",
            }

        n = len(valid)
        avg_tech = sum(s.get("technical_accuracy", 0) for s in valid) / n
        avg_clarity = sum(s.get("clarity", 0) for s in valid) / n
        avg_comm = sum(s.get("communication", 0) for s in valid) / n

        overall = (
            avg_tech * self.weights["technical_accuracy"]
            + avg_clarity * self.weights["clarity"]
            + avg_comm * self.weights["communication"]
        )

        all_strengths = []
        all_weaknesses = []
        for s in valid:
            all_strengths.extend(s.get("strengths", []))
            all_weaknesses.extend(s.get("weaknesses", []))

        return {
            "overall_score": round(overall, 1),
            "avg_technical": round(avg_tech, 1),
            "avg_clarity": round(avg_clarity, 1),
            "avg_communication": round(avg_comm, 1),
            "total_questions": n,
            "all_strengths": list(dict.fromkeys(all_strengths))[:10],
            "all_weaknesses": list(dict.fromkeys(all_weaknesses))[:10],
        }

    @staticmethod
    def _empty_response(reason: str) -> dict:
        return {
            "score": 0,
            "technical_accuracy": 0,
            "clarity": 0,
            "communication": 0,
            "weighted_score": 0,
            "strengths": [],
            "weaknesses": [reason],
            "suggested_improvement": "Please provide a more detailed answer.",
        }
