"""Feature 11: Resume Parser — Complete structured resume extraction.

Uses LLM to parse a resume into structured sections: contact, education,
experience, skills, projects, certifications.
"""
import logging
from datetime import datetime

from src.career.json_utils import career_llm_call, safe_llm_json

logger = logging.getLogger("ResumeParser")

# ── In-memory resume store ───────────────────────────────────────────
_resume_store: list[dict] = []


def parse_resume(llm, raw_text: str, label: str = "") -> dict:
    """Parse a resume into structured JSON via LLM.

    Args:
        llm: A llama_cpp.Llama model instance.
        raw_text: Full resume text.
        label: Optional label for this resume.

    Returns:
        dict with structured resume data.
    """
    prompt = f"""You are an expert resume parser. Extract ALL structured information from this resume.

RESUME TEXT:
{raw_text[:4000]}

Respond ONLY with valid JSON matching this EXACT structure:
{{
  "name": "<full name>",
  "email": "<email or 'not found'>",
  "phone": "<phone or 'not found'>",
  "links": {{
    "linkedin": "<url or ''>",
    "github": "<url or ''>",
    "portfolio": "<url or ''>",
    "other": ["<any other links>"]
  }},
  "summary": "<professional summary if present, else ''>",
  "education": [
    {{
      "institution": "<school name>",
      "degree": "<degree type and major>",
      "dates": "<date range>",
      "gpa": "<GPA or ''>",
      "relevant_courses": ["<course1>", "<course2>"]
    }}
  ],
  "experience": [
    {{
      "company": "<company name>",
      "role": "<job title>",
      "dates": "<date range>",
      "location": "<location or ''>",
      "bullets": ["<achievement/responsibility>"]
    }}
  ],
  "skills": {{
    "languages": ["<programming languages>"],
    "frameworks": ["<frameworks/libraries>"],
    "tools": ["<tools/platforms>"],
    "soft_skills": ["<soft skills>"],
    "other": ["<other skills>"]
  }},
  "projects": [
    {{
      "name": "<project name>",
      "description": "<what it does>",
      "tech_stack": ["<technologies>"],
      "dates": "<date range or ''>"
    }}
  ],
  "certifications": [
    {{
      "name": "<cert name>",
      "issuer": "<issuing body>",
      "date": "<date or ''>"
    }}
  ]
}}"""

    try:
        text = career_llm_call(llm, prompt, max_tokens=2000, temperature=0.2)
        result = safe_llm_json(text, expect="object")
        if result is not None:
            parsed = {
                "id": len(_resume_store) + 1,
                "label": label or result.get("name", f"Resume-{len(_resume_store) + 1}"),
                "raw_text": raw_text,
                "parsed": result,
                "parsed_at": datetime.now().isoformat(),
            }
            _resume_store.append(parsed)
            return parsed
    except Exception as e:
        logger.error(f"Resume parsing failed: {e}")

    return {"error": "Failed to parse resume"}


def list_parsed_resumes() -> list[dict]:
    """List all parsed resumes (without raw text)."""
    return [
        {"id": r["id"], "label": r["label"], "parsed_at": r["parsed_at"]}
        for r in _resume_store
    ]


def get_parsed_resume(resume_id: int) -> dict | None:
    """Get a parsed resume by ID."""
    for r in _resume_store:
        if r["id"] == resume_id:
            return r
    return None


def clear_resumes() -> None:
    """Clear all stored parsed resumes."""
    _resume_store.clear()
