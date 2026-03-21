"""Feature 6: Project Extraction & Ranking.

6A: Extract structured project data from raw text.
6C: Rank and score projects against a job description.
"""
import json
import logging
import re

logger = logging.getLogger("ProjectManager")


def extract_projects(llm, raw_text: str) -> list[dict]:
    """Extract structured project data from raw text via LLM.

    Args:
        llm: A llama_cpp.Llama model instance.
        raw_text: Raw text containing project descriptions (from resume or free text).

    Returns:
        list of dicts, each with name, description, tech_stack, impact, dates.
    """
    prompt = f"""You are a resume parser specializing in extracting project information.

TEXT:
{raw_text[:3000]}

Extract ALL projects mentioned. For each project, identify:
- name: project title
- description: 1-2 sentence summary of what it does
- tech_stack: list of technologies used
- impact: quantifiable impact or result (if mentioned)
- dates: when it was built (if mentioned)

Respond ONLY with valid JSON:
[
  {{
    "name": "<project name>",
    "description": "<what it does>",
    "tech_stack": ["tech1", "tech2"],
    "impact": "<measurable result or 'not specified'>",
    "dates": "<date range or 'not specified'>"
  }}
]"""

    try:
        response = llm.create_completion(
            prompt=prompt,
            max_tokens=800,
            temperature=0.2,
            stop=["</s>", "USER:", "ASSISTANT:"],
        )
        text = response["choices"][0]["text"].strip()
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        logger.error(f"Project extraction failed: {e}")

    return []


def rank_projects(llm, projects: list[dict], jd_text: str) -> list[dict]:
    """Rank and score projects against a job description via LLM.

    Args:
        llm: A llama_cpp.Llama model instance.
        projects: List of project dicts (from extract_projects or manual input).
        jd_text: Full job description text.

    Returns:
        list of dicts with name, relevance_score, reasoning, highlight_suggestion.
    """
    if not projects:
        return []

    projects_str = json.dumps(projects[:10], indent=2)  # Limit to 10 projects

    prompt = f"""You are a career advisor. Rank these projects by relevance to the job description.

PROJECTS:
{projects_str}

JOB DESCRIPTION:
{jd_text[:2000]}

For each project, provide a relevance score and reasoning. Order from most to least relevant.

Respond ONLY with valid JSON:
[
  {{
    "name": "<project name>",
    "relevance_score": <0-100>,
    "reasoning": "<why this project is relevant or not>",
    "highlight_suggestion": "<how to present this project on the resume>"
  }}
]"""

    try:
        response = llm.create_completion(
            prompt=prompt,
            max_tokens=800,
            temperature=0.3,
            stop=["</s>", "USER:", "ASSISTANT:"],
        )
        text = response["choices"][0]["text"].strip()
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except Exception as e:
        logger.error(f"Project ranking failed: {e}")

    return []
