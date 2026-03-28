"""Feature 5: Recruiter Eye Simulator.

Simulates how a tough recruiter would perceive a resume against a JD.
"""
import logging

from src.career.json_utils import career_llm_call, safe_llm_json

logger = logging.getLogger("RecruiterSim")


def simulate_recruiter(llm, resume_text: str, jd_text: str) -> dict:
    """Simulate a critical recruiter's evaluation via LLM.

    Args:
        llm: A llama_cpp.Llama model instance.
        resume_text: Full resume text.
        jd_text: Full job description text.

    Returns:
        dict with verdict, confidence, six_second_impression,
        relevance_score, presentation_score, strengths, red_flags,
        interview_questions, tips_for_candidate, recruiter_notes.
    """
    prompt = f"""You are a highly experienced, blunt technical recruiter who reviews 200+ resumes per day.
You have 6 seconds to form an initial impression.

RESUME:
{resume_text[:2000]}

JOB DESCRIPTION:
{jd_text[:1500]}

Give your raw, unfiltered assessment. Be specific and brutally honest.

Respond ONLY with valid JSON:
{{
  "verdict": "<SHORTLIST|MAYBE|REJECT>",
  "confidence": <0-100>,
  "six_second_impression": "<what you noticed in the first 6 seconds>",
  "relevance_score": <0-100>,
  "presentation_score": <0-100>,
  "strengths": ["strength1", "strength2"],
  "red_flags": ["flag1", "flag2"],
  "interview_questions": ["question you'd ask in screening"],
  "tips_for_candidate": ["actionable improvement tip"],
  "recruiter_notes": "<internal notes you'd write>"
}}"""

    try:
        text = career_llm_call(llm, prompt, max_tokens=1500, temperature=0.4)
        result = safe_llm_json(text, expect="object")
        if result is not None:
            return result
        logger.warning("Recruiter sim: LLM output could not be parsed as JSON")
    except Exception as e:
        logger.error(f"Recruiter simulation failed: {e}")

    return {"error": "Failed to simulate recruiter review"}
