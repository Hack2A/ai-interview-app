"""Feature 2: AI Cover Letter Generator.

Generates a tailored cover letter based on resume, JD, and tone.
Supports 10 tone presets plus a custom free-text tone.
"""
import logging

from src.career.json_utils import career_llm_call, safe_llm_json

logger = logging.getLogger("CoverLetter")

TONE_INSTRUCTIONS = {
    "professional": "Use a formal, polished tone appropriate for corporate roles.",
    "enthusiastic": "Use an energetic, passionate tone that conveys genuine excitement.",
    "concise": "Keep it under 200 words. Every sentence must add value.",
    "storytelling": "Weave the candidate's experience into a compelling narrative arc.",
    "startup": (
        "Write like a builder talking to builders. Show you move fast, "
        "wear multiple hats, and care about impact over titles. "
        "Use energetic, direct language — no corporate fluff."
    ),
    "faang": (
        "Emphasize scale, data-driven decisions, and measurable impact. "
        "Show algorithmic thinking and system design awareness. "
        "Use precise, metric-heavy language. Mention complexity and scope."
    ),
    "service_based": (
        "Highlight client-facing skills, delivery excellence, and adaptability. "
        "Show experience with cross-functional teams, SLAs, and stakeholder management. "
        "Use a reliable, structured tone."
    ),
    "product_based": (
        "Focus on product thinking, user empathy, and end-to-end ownership. "
        "Show how you shipped features that moved metrics. "
        "Use outcome-oriented language with a bias toward experiments and data."
    ),
    "quant": (
        "Write with mathematical precision. Highlight quantitative skills, "
        "statistical modeling, optimization, and analytical rigor. "
        "Use concise, technical language. Mention specific tools, frameworks, and methodologies."
    ),
}

VALID_TONES = set(TONE_INSTRUCTIONS.keys()) | {"custom"}


def generate_cover_letter(llm, resume_text: str, jd_text: str,
                          tone: str = "professional",
                          custom_instruction: str = "") -> dict:
    """Generate a cover letter via LLM.

    Args:
        llm: A llama_cpp.Llama model instance.
        resume_text: Full resume text.
        jd_text: Full job description text.
        tone: One of the preset tones or 'custom'.
        custom_instruction: Free-text tone description (used when tone='custom').

    Returns:
        dict with cover_letter text and tone used.
    """
    if tone == "custom" and custom_instruction.strip():
        tone_line = custom_instruction.strip()
    elif tone in TONE_INSTRUCTIONS:
        tone_line = TONE_INSTRUCTIONS[tone]
    else:
        tone = "professional"
        tone_line = TONE_INSTRUCTIONS["professional"]

    prompt = f"""You are an expert cover letter writer. Generate a cover letter for this candidate.

RESUME:
{resume_text[:3000]}

JOB DESCRIPTION:
{jd_text[:2000]}

TONE: {tone}
{tone_line}

Write a complete cover letter (3-4 paragraphs). Do NOT include placeholders like [Company Name].
Infer the company and role from the JD. Include specific skills and experiences from the resume
that match the JD requirements.

Respond ONLY with valid JSON:
{{
  "cover_letter": "<full cover letter text>",
  "tone_used": "{tone}"
}}"""

    try:
        text = career_llm_call(llm, prompt, max_tokens=1500, temperature=0.5)
        result = safe_llm_json(text, expect="object")
        if result is not None:
            return result
    except Exception as e:
        logger.error(f"Cover letter generation failed: {e}")

    return {"error": "Failed to generate cover letter"}
