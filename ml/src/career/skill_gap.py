"""Feature 3: Skill Gap Analyzer.

Identifies missing skills and generates a comprehensive learning plan with
gap severity, skill categories, resources, certifications, and resume tips.
"""
import logging

from src.career.json_utils import career_llm_call, safe_llm_json

logger = logging.getLogger("SkillGap")


def analyze_skill_gap(llm, resume_text: str, jd_text: str,
                      match_json: dict | None = None,
                      current_date: str = "2026-03") -> dict:
    """Analyze skill gaps with full roadmap-style output via LLM.

    Args:
        llm: A llama_cpp.Llama model instance.
        resume_text: Full resume text.
        jd_text: Full job description text.
        match_json: Optional match report dict from Feature 1.
        current_date: Current date string for context.

    Returns:
        dict with skills_present, skills_missing, learning_roadmap,
        recommended_certifications, resume_tips.
    """
    context = ""
    if match_json and "missing_keywords" in match_json:
        context = f"\nPrevious analysis identified these missing keywords: {', '.join(match_json['missing_keywords'][:10])}"

    prompt = f"""You are a career development advisor. Analyze the skill gap between this resume and job description.

RESUME:
{resume_text[:2000]}

JOB DESCRIPTION:
{jd_text[:1500]}
{context}

Respond ONLY with valid JSON:
{{
  "skills_present": ["skill1", "skill2"],
  "skills_missing": [
    {{"skill": "<name>", "severity": "<critical|high|medium|low>"}}
  ],
  "learning_plan": [
    {{"skill": "<name>", "priority": "<must_learn|should_learn|nice_to_know>", "estimated_weeks": <number>, "resource": "<course or resource name>"}}
  ],
  "certifications": ["<certification name>"],
  "resume_tips": ["<actionable tip>"]
}}"""

    try:
        text = career_llm_call(llm, prompt, max_tokens=2500, temperature=0.3)
        result = safe_llm_json(text, expect="object")
        if result is not None:
            return result
        logger.warning("Skill gap: LLM output could not be parsed as JSON")
    except Exception as e:
        logger.error(f"Skill gap analysis failed: {e}")

    return {"error": "Failed to analyze skill gap"}
