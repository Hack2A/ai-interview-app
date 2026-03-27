"""Feature 3: Skill Gap Analyzer.

Identifies missing skills and generates a prioritized learning plan.
"""
import json
import logging
import re

logger = logging.getLogger("SkillGap")


def analyze_skill_gap(llm, resume_text: str, jd_text: str,
                      match_json: dict | None = None,
                      current_date: str = "2026-03") -> dict:
    """Analyze skill gaps and produce an upskilling plan via LLM.

    Args:
        llm: A llama_cpp.Llama model instance.
        resume_text: Full resume text.
        jd_text: Full job description text.
        match_json: Optional match report dict from Feature 1.
        current_date: Current date string for context.

    Returns:
        dict with matched_skills, missing_skills, learning_plan,
        estimated_time, priority_order, free_resources.
    """
    context = ""
    if match_json and "missing_keywords" in match_json:
        context = f"\nPrevious analysis identified these missing keywords: {', '.join(match_json['missing_keywords'][:10])}"

    prompt = f"""You are a career development advisor. Analyze the skill gap between this resume and job description.

RESUME:
{resume_text[:3000]}

JOB DESCRIPTION:
{jd_text[:2000]}
{context}

Current date: {current_date}

Respond ONLY with valid JSON:
{{
  "matched_skills": ["skill1", "skill2"],
  "missing_skills": ["skill1", "skill2"],
  "learning_plan": [
    {{
      "skill": "<skill name>",
      "priority": "<high|medium|low>",
      "estimated_weeks": <number>,
      "recommended_approach": "<description>"
    }}
  ],
  "estimated_total_weeks": <number>,
  "priority_order": ["skill1", "skill2"],
  "free_resources": [
    {{
      "skill": "<skill name>",
      "resource": "<resource name or URL>",
      "type": "<course|doc|tutorial|video>"
    }}
  ]
}}"""

    try:
        response = llm.create_completion(
            prompt=prompt,
            max_tokens=1000,
            temperature=0.3,
            stop=["</s>", "USER:", "ASSISTANT:"],
        )
        text = response["choices"][0]["text"].strip()
        match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        logger.error(f"Skill gap analysis failed: {e}")

    return {"error": "Failed to analyze skill gap"}
