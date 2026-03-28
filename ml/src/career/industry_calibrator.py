"""Feature 7: Industry Calibrator.

Adjusts resume language and emphasis based on target industry norms.
"""
import logging

from src.career.json_utils import career_llm_call, safe_llm_json

logger = logging.getLogger("IndustryCalibrator")

MODES = {
    "startup": "Emphasize speed, scrappiness, wearing multiple hats, and impact metrics. Prefer action verbs like 'shipped', 'built', 'launched'.",
    "enterprise": "Emphasize process, scale, cross-functional collaboration, and compliance. Use formal language like 'managed', 'optimized', 'governed'.",
    "faang": "Emphasize algorithmic thinking, system design, scale, and data-driven decisions. Highlight Big-O complexity, metrics, and impact at scale.",
    "consulting": "Emphasize client-facing skills, problem-solving frameworks, deliverables, and stakeholder management.",
    "academic": "Emphasize research publications, methodologies, teaching, grants, and peer-reviewed contributions.",
    "government": "Emphasize compliance, clearances, structured processes, policy implementation, and public service impact.",
}


def calibrate_industry(llm, resume_text: str, mode: str = "startup") -> dict:
    """Calibrate resume language for a target industry via LLM.

    Args:
        llm: A llama_cpp.Llama model instance.
        resume_text: Full resume text.
        mode: Target industry — one of startup|enterprise|faang|consulting|academic|government.

    Returns:
        dict with target_industry, tone_adjustments, rewritten_bullets,
        keywords_to_add, keywords_to_remove, overall_advice.
    """
    if mode not in MODES:
        mode = "startup"

    instruction = MODES[mode]

    prompt = f"""You are a resume strategist specializing in industry-specific optimization.

RESUME:
{resume_text[:2000]}

TARGET INDUSTRY: {mode}
INSTRUCTION: {instruction}

Analyze this resume and suggest how to calibrate it for the target industry.

Respond ONLY with valid JSON:
{{
  "target_industry": "{mode}",
  "tone_adjustments": ["adjustment1", "adjustment2"],
  "rewritten_bullets": [
    {{
      "original": "<original bullet point>",
      "rewritten": "<industry-calibrated version>",
      "reasoning": "<why this change>"
    }}
  ],
  "keywords_to_add": ["keyword1", "keyword2"],
  "keywords_to_remove": ["keyword1", "keyword2"],
  "overall_advice": "<2-3 sentences of strategic advice>"
}}"""

    try:
        text = career_llm_call(llm, prompt, max_tokens=2000, temperature=0.3)
        result = safe_llm_json(text, expect="object")
        if result is not None:
            return result
        logger.warning("Industry calibrator: LLM output could not be parsed as JSON")
    except Exception as e:
        logger.error(f"Industry calibration failed: {e}")

    return {"error": "Failed to calibrate for industry"}
