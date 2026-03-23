"""Feature 2: AI Cover Letter Generator.

Generates a tailored cover letter based on resume, JD, and tone.
"""
import json
import logging
import re

logger = logging.getLogger("CoverLetter")

VALID_TONES = {"professional", "enthusiastic", "concise", "storytelling"}


def generate_cover_letter(llm, resume_text: str, jd_text: str,
                          tone: str = "professional") -> dict:
    """Generate a cover letter via LLM.

    Args:
        llm: A llama_cpp.Llama model instance.
        resume_text: Full resume text.
        jd_text: Full job description text.
        tone: One of professional|enthusiastic|concise|storytelling.

    Returns:
        dict with cover_letter text.
    """
    if tone not in VALID_TONES:
        tone = "professional"

    tone_instructions = {
        "professional": "Use a formal, polished tone appropriate for corporate roles.",
        "enthusiastic": "Use an energetic, passionate tone that conveys genuine excitement.",
        "concise": "Keep it under 200 words. Every sentence must add value.",
        "storytelling": "Weave the candidate's experience into a compelling narrative arc.",
    }

    prompt = f"""You are an expert cover letter writer. Generate a cover letter for this candidate.

RESUME:
{resume_text[:3000]}

JOB DESCRIPTION:
{jd_text[:2000]}

TONE: {tone}
{tone_instructions[tone]}

Write a complete cover letter (3-4 paragraphs). Do NOT include placeholders like [Company Name].
Infer the company and role from the JD. Include specific skills and experiences from the resume
that match the JD requirements.

Respond ONLY with valid JSON:
{{
  "cover_letter": "<full cover letter text>"
}}"""

    try:
        response = llm.create_completion(
            prompt=prompt,
            max_tokens=1000,
            temperature=0.5,
            stop=["</s>", "USER:", "ASSISTANT:"],
        )
        text = response["choices"][0]["text"].strip()
        match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        logger.error(f"Cover letter generation failed: {e}")

    return {"error": "Failed to generate cover letter"}
