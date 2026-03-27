"""Feature 1: Smart Resume–JD Match Report.

Generates a structured compatibility analysis between a resume and job description.
"""
import json
import logging
import re

logger = logging.getLogger("MatchReport")


def generate_match_report(llm, resume_text: str, jd_text: str) -> dict:
    """Generate a detailed resume-JD match report via LLM.

    Args:
        llm: A llama_cpp.Llama model instance.
        resume_text: Full resume text.
        jd_text: Full job description text.

    Returns:
        dict with overall_score, skill_match_score, experience_alignment,
        matched_keywords, missing_keywords, strengths, weaknesses,
        recommendations, fit_summary, confidence_level.
    """
    prompt = f"""You are a senior career advisor. Analyze the compatibility between this resume and job description.

RESUME:
{resume_text[:3000]}

JOB DESCRIPTION:
{jd_text[:2000]}

Respond ONLY with valid JSON containing these exact keys:
{{
  "overall_score": <0-100>,
  "skill_match_score": <0-100>,
  "experience_alignment": "<low|medium|high>",
  "matched_keywords": ["keyword1", "keyword2"],
  "missing_keywords": ["keyword1", "keyword2"],
  "strengths": ["strength1", "strength2"],
  "weaknesses": ["weakness1", "weakness2"],
  "recommendations": ["rec1", "rec2"],
  "fit_summary": "<2-3 sentence summary>",
  "confidence_level": "<low|medium|high>"
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
        logger.error(f"Match report generation failed: {e}")

    return {"error": "Failed to generate match report"}
