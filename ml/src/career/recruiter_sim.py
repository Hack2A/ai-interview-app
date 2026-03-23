"""Feature 5: Recruiter Eye Simulator.

Simulates a recruiter reviewing the resume against the JD.
"""
import json
import logging
import re

logger = logging.getLogger("RecruiterSim")


def simulate_recruiter(llm, resume_text: str, jd_text: str,
                       current_date: str = "2026-03") -> dict:
    """Simulate a recruiter's first-pass review via LLM.

    Args:
        llm: A llama_cpp.Llama model instance.
        resume_text: Full resume text.
        jd_text: Full job description text.
        current_date: Current date string for context.

    Returns:
        dict with verdict, scores, strengths, red_flags,
        interview_questions, tips.
    """
    prompt = f"""You are a senior tech recruiter with 10+ years of experience. You are reviewing a resume for a specific role.
Perform a realistic recruiter first-pass: spend 6 seconds scanning, then do a deep read.

RESUME:
{resume_text[:3000]}

JOB DESCRIPTION:
{jd_text[:2000]}

Current date: {current_date}

Respond ONLY with valid JSON:
{{
  "verdict": "<SHORTLIST|MAYBE|REJECT>",
  "confidence": <0-100>,
  "six_second_impression": "<what caught your eye in 6 seconds>",
  "relevance_score": <0-100>,
  "presentation_score": <0-100>,
  "strengths": ["strength1", "strength2", "strength3"],
  "red_flags": ["flag1", "flag2"],
  "interview_questions": ["question1", "question2", "question3"],
  "tips_for_candidate": ["tip1", "tip2", "tip3"],
  "recruiter_notes": "<internal notes a recruiter would write>"
}}"""

    try:
        response = llm.create_completion(
            prompt=prompt,
            max_tokens=800,
            temperature=0.3,
            stop=["</s>", "USER:", "ASSISTANT:"],
        )
        text = response["choices"][0]["text"].strip()
        match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        logger.error(f"Recruiter simulation failed: {e}")

    return {"error": "Failed to run recruiter simulation"}
