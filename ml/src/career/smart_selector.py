"""Feature 12: Smart Selector — Resume × JD × Projects → Ranked LaTeX.

Lets the user select a parsed resume, a stored JD, and their project list,
then ranks all projects against the JD and generates LaTeX code.
"""
import json
import logging

from src.career.json_utils import safe_llm_json

logger = logging.getLogger("SmartSelector")


def select_and_rank(llm, resume_parsed: dict, jd_text: str,
                    extra_projects: list[dict] | None = None) -> dict:
    """Rank all projects (from resume + extra) against a JD, and return LaTeX.

    Args:
        llm: A llama_cpp.Llama model instance.
        resume_parsed: The 'parsed' dict from resume_parser.
        jd_text: Full JD text.
        extra_projects: Additional projects from the project store.

    Returns:
        dict with ranked_projects and latex_code.
    """
    from src.career.project_manager import rank_projects, generate_project_latex

    # Collect projects from resume
    resume_projects = resume_parsed.get("projects", [])
    # Normalize resume projects to have consistent keys
    normalized = []
    for p in resume_projects:
        normalized.append({
            "name": p.get("name", "Untitled"),
            "description": p.get("description", ""),
            "tech_stack": p.get("tech_stack", []),
            "impact": p.get("impact", "not specified"),
            "dates": p.get("dates", ""),
            "source": "resume",
        })

    # Add extra (manually added / GitHub-extracted) projects
    if extra_projects:
        for p in extra_projects:
            normalized.append({
                "name": p.get("name", "Untitled"),
                "description": p.get("description", ""),
                "tech_stack": p.get("tech_stack", []),
                "impact": p.get("impact", "not specified"),
                "dates": p.get("dates", ""),
                "github_link": p.get("github_link", ""),
                "source": p.get("source", "manual"),
            })

    if not normalized:
        return {"error": "No projects found to rank"}

    # Rank using the project manager
    ranked = rank_projects(llm, normalized, jd_text)

    # Merge rank data back into project details for LaTeX
    rank_map = {r["name"]: r for r in ranked}
    ordered_projects = []
    for r in ranked:
        # Find the original project data
        original = next((p for p in normalized if p["name"] == r["name"]), {})
        merged = {**original, **r}
        ordered_projects.append(merged)

    # Generate LaTeX
    latex = generate_project_latex(ordered_projects)

    return {
        "total_projects": len(normalized),
        "ranked_projects": ranked,
        "latex_code": latex,
    }
