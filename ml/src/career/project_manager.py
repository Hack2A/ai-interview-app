"""Feature 6: Project Extraction, Ranking, Manual Entry, GitHub Import & LaTeX.

6A: Extract structured project data from raw text.
6B: Add projects manually with validated fields.
6C: Rank and score projects against a job description.
6D: Extract project info from a public GitHub repository URL.
6E: Generate LaTeX code for projects in Google XYZ format.
"""
import json
import logging
import re

from src.career.json_utils import career_llm_call, safe_llm_json

logger = logging.getLogger("ProjectManager")

# ── In-memory project store ──────────────────────────────────────────
_project_store: list[dict] = []


def _next_id() -> int:
    return max((p.get("id", 0) for p in _project_store), default=0) + 1


# ── 6A: Extract from text ───────────────────────────────────────────

def extract_projects(llm, raw_text: str) -> list[dict]:
    """Extract structured project data from raw text via LLM."""
    prompt = f"""You are a resume parser specializing in extracting project information.

TEXT:
{raw_text[:3000]}

Extract ALL projects mentioned. For each project, identify:
- name: project title
- description: 1-2 sentence summary of what it does
- tech_stack: list of technologies used
- impact: quantifiable impact or result (if mentioned)
- dates: when it was built (if mentioned)

Respond ONLY with a valid JSON array:
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
        text = career_llm_call(llm, prompt, max_tokens=2000, temperature=0.2)
        result = safe_llm_json(text, expect="array")
        if result is not None:
            # Store extracted projects
            for proj in result:
                proj["id"] = _next_id()
                proj["source"] = "resume_extraction"
                _project_store.append(proj)
            return result
        logger.warning("Project extraction: LLM output could not be parsed as JSON")
    except Exception as e:
        logger.error(f"Project extraction failed: {e}")

    return []


# ── 6B: Manual project entry ────────────────────────────────────────

REQUIRED_FIELDS = {"title", "description"}
OPTIONAL_FIELDS = {"skills_used", "tools_used", "github_link", "dates",
                   "impact", "role", "team_size"}


def add_project_manual(fields: dict) -> dict:
    """Add a project manually with validated fields.

    Required: title, description.
    Optional: skills_used, tools_used, github_link, dates, impact, role, team_size.
    """
    missing = REQUIRED_FIELDS - set(fields.keys())
    if missing:
        return {"error": f"Missing required fields: {', '.join(missing)}"}

    project = {
        "id": _next_id(),
        "name": fields["title"],
        "description": fields["description"],
        "tech_stack": fields.get("skills_used", []),
        "tools": fields.get("tools_used", []),
        "github_link": fields.get("github_link", ""),
        "dates": fields.get("dates", "not specified"),
        "impact": fields.get("impact", "not specified"),
        "role": fields.get("role", ""),
        "team_size": fields.get("team_size", ""),
        "source": "manual",
    }
    _project_store.append(project)
    return project


# ── 6C: Rank projects ───────────────────────────────────────────────

def rank_projects(llm, projects: list[dict], jd_text: str) -> list[dict]:
    """Rank and score projects against a job description via LLM."""
    if not projects:
        return []

    # Slim down project data to avoid token overflow
    slim_projects = []
    for p in projects[:10]:
        slim_projects.append({
            "name": p.get("name", "Untitled"),
            "description": p.get("description", "")[:200],
            "tech_stack": p.get("tech_stack", []),
        })
    projects_str = json.dumps(slim_projects, indent=2)

    prompt = f"""You are a career advisor. Rank these projects by relevance to the job description.

PROJECTS:
{projects_str}

JOB DESCRIPTION:
{jd_text[:2000]}

For each project, provide a relevance score and reasoning. Order from most to least relevant.

Respond ONLY with a valid JSON array:
[
  {{
    "name": "<project name>",
    "relevance_score": <0-100>,
    "reasoning": "<why this project is relevant or not>",
    "highlight_suggestion": "<how to present this project on the resume>"
  }}
]"""

    try:
        text = career_llm_call(llm, prompt, max_tokens=2000, temperature=0.3)
        result = safe_llm_json(text, expect="array")
        if result is not None:
            return result
        logger.warning("rank_projects: LLM returned unparseable JSON")
    except Exception as e:
        logger.error(f"Project ranking failed: {e}")

    return []


# ── 6D: GitHub extraction ───────────────────────────────────────────

def extract_from_github(repo_url: str) -> dict:
    """Extract project info from a public GitHub repo URL.

    Uses the GitHub REST API (no auth needed for public repos).
    Set GITHUB_TOKEN env var to avoid rate limiting.
    """
    try:
        import requests
    except ImportError:
        return {"error": "requests library not installed. Run: pip install requests"}

    import os

    # Parse owner/repo from URL
    match = re.match(
        r"https?://github\.com/([^/]+)/([^/]+)/?", repo_url.strip()
    )
    if not match:
        return {"error": f"Invalid GitHub URL: {repo_url}"}

    owner, repo = match.group(1), match.group(2).rstrip(".git")
    api_url = f"https://api.github.com/repos/{owner}/{repo}"

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "intrv-ai-career-suite/1.0",
    }
    token = os.environ.get("GITHUB_TOKEN", "")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        resp = requests.get(api_url, headers=headers, timeout=10)
        if resp.status_code == 404:
            return {"error": f"Repo not found or private: {owner}/{repo}. If private, set GITHUB_TOKEN env var."}
        if resp.status_code == 403:
            return {"error": "GitHub API rate limit hit. Set GITHUB_TOKEN env var or wait a few minutes."}
        if resp.status_code != 200:
            return {"error": f"GitHub API returned {resp.status_code}: {resp.text[:200]}"}

        data = resp.json()
        project = {
            "id": _next_id(),
            "name": data.get("name", repo),
            "description": data.get("description", "") or "",
            "tech_stack": [data["language"]] if data.get("language") else [],
            "topics": data.get("topics", []),
            "stars": data.get("stargazers_count", 0),
            "forks": data.get("forks_count", 0),
            "last_updated": data.get("updated_at", ""),
            "github_link": repo_url.strip(),
            "homepage": data.get("homepage", ""),
            "source": "github_api",
        }

        # Try to get languages breakdown
        lang_resp = requests.get(f"{api_url}/languages", headers=headers, timeout=10)
        if lang_resp.status_code == 200:
            project["tech_stack"] = list(lang_resp.json().keys())

        _project_store.append(project)
        return project
    except Exception as e:
        logger.error(f"GitHub extraction failed: {e}")
        return {"error": f"GitHub extraction failed: {e}"}


# ── 6E: LaTeX generation (Google XYZ format) ─────────────────────────

def generate_project_latex(projects: list[dict], format: str = "xyz") -> str:
    r"""Generate LaTeX code for project entries.

    Uses Google's XYZ format:
    "Accomplished [X] as measured by [Y], by doing [Z]"

    Returns a LaTeX string ready to paste into a resume .tex file.
    """
    lines = [r"\section{Projects}", ""]

    for proj in projects:
        name = proj.get("name", "Untitled Project")
        tech = proj.get("tech_stack", [])
        desc = proj.get("description", "")
        impact = proj.get("impact", "")
        dates = proj.get("dates", "")
        github = proj.get("github_link", "")

        tech_str = ", ".join(tech) if tech else ""

        lines.append(r"\resumeProjectHeading")
        if github:
            lines.append(
                f"  {{\\textbf{{{name}}} $|$ "
                f"\\emph{{{tech_str}}} $|$ "
                f"\\href{{{github}}}{{\\underline{{GitHub}}}}}}"
                f"{{{dates}}}"
            )
        else:
            lines.append(
                f"  {{\\textbf{{{name}}} $|$ "
                f"\\emph{{{tech_str}}}}}"
                f"{{{dates}}}"
            )

        lines.append(r"  \resumeItemListStart")
        if desc:
            lines.append(f"    \\resumeItem{{{desc}}}")
        if impact and impact != "not specified":
            lines.append(f"    \\resumeItem{{Impact: {impact}}}")
        lines.append(r"  \resumeItemListEnd")
        lines.append("")

    return "\n".join(lines)


# ── Helpers ──────────────────────────────────────────────────────────

def get_all_projects() -> list[dict]:
    """Return all stored projects."""
    return list(_project_store)


def update_project(project_id: int, updates: dict) -> dict | None:
    """Update fields of an existing project by ID."""
    for proj in _project_store:
        if proj.get("id") == project_id:
            proj.update(updates)
            return proj
    return None


def clear_projects() -> None:
    """Clear the in-memory project store."""
    _project_store.clear()
