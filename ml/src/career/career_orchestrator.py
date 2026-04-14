"""Career Orchestrator — central entry point for all career features.

Lazy-loads the LLM and delegates to feature-specific modules.
"""
import json
import logging

from src.brain.llm_engine import OllamaClient, OLLAMA_CAREER_MODEL

from config import settings

logger = logging.getLogger("CareerOrchestrator")

# Career features need a larger context window than the interview engine
# because prompts include full resume + JD text + JSON schema instructions.
# With n_ctx=4096, the prompt alone can consume ~3500 tokens, leaving only
# ~500 for the response — causing truncated JSON output from every feature.
CAREER_CONTEXT_SIZE = 8192


class CareerOrchestrator:
    """Orchestrates all career management features with a shared LLM."""

    def __init__(self) -> None:
        self._llm: OllamaClient | None = None

    @property
    def llm(self) -> OllamaClient:
        """Lazy-load the LLM model with a larger context for career features."""
        if self._llm is None:
            ctx = CAREER_CONTEXT_SIZE
            logger.info(f"Connecting to Ollama (context size constraint ignored in proxy)")
            self._llm = OllamaClient(model_name=OLLAMA_CAREER_MODEL)
            logger.info(f"Ollama LLM client {OLLAMA_CAREER_MODEL} loaded for Career features")
        return self._llm

    # ── Feature 1: Match Report ───────────────────────────────────

    def match_report(self, resume_text: str, jd_text: str) -> dict:
        from src.career.match_report import generate_match_report
        return generate_match_report(self.llm, resume_text, jd_text)

    # ── Feature 2: Cover Letter ───────────────────────────────────

    def cover_letter(self, resume_text: str, jd_text: str,
                     tone: str = "professional",
                     custom_instruction: str = "") -> dict:
        from src.career.cover_letter import generate_cover_letter
        return generate_cover_letter(self.llm, resume_text, jd_text,
                                     tone, custom_instruction)

    # ── Feature 3: Skill Gap ──────────────────────────────────────

    def skill_gap(self, resume_text: str, jd_text: str,
                  match_json: dict | None = None) -> dict:
        from src.career.skill_gap import analyze_skill_gap
        return analyze_skill_gap(self.llm, resume_text, jd_text, match_json)

    # ── Feature 4: Learning Roadmap ───────────────────────────────

    def roadmap(self, topic: str, context: str = "") -> dict:
        from src.career.roadmap_builder import build_roadmap
        return build_roadmap(self.llm, topic, context)

    # ── Feature 5: Recruiter Simulator ────────────────────────────

    def recruiter_sim(self, resume_text: str, jd_text: str) -> dict:
        from src.career.recruiter_sim import simulate_recruiter
        return simulate_recruiter(self.llm, resume_text, jd_text)

    # ── Feature 6A: Extract Projects ──────────────────────────────

    def extract_projects(self, raw_text: str) -> list[dict]:
        from src.career.project_manager import extract_projects
        return extract_projects(self.llm, raw_text)

    # ── Feature 6B: Add Project Manually ──────────────────────────

    @staticmethod
    def add_project_manual(fields: dict) -> dict:
        from src.career.project_manager import add_project_manual
        return add_project_manual(fields)

    # ── Feature 6C: Rank Projects ─────────────────────────────────

    def rank_projects(self, projects: list[dict], jd_text: str) -> list[dict]:
        from src.career.project_manager import rank_projects
        return rank_projects(self.llm, projects, jd_text)

    # ── Feature 6D: Extract from GitHub ───────────────────────────

    @staticmethod
    def extract_project_github(repo_url: str) -> dict:
        from src.career.project_manager import extract_from_github
        return extract_from_github(repo_url)

    # ── Feature 6E: Generate LaTeX ────────────────────────────────

    @staticmethod
    def generate_project_latex(projects: list[dict]) -> str:
        from src.career.project_manager import generate_project_latex
        return generate_project_latex(projects)

    # ── Feature 6F: Get All Projects ──────────────────────────────

    @staticmethod
    def get_all_projects() -> list[dict]:
        from src.career.project_manager import get_all_projects
        return get_all_projects()

    # ── Feature 7: Industry Calibrator ────────────────────────────

    def industry_calibrate(self, resume_text: str, mode: str = "startup") -> dict:
        from src.career.industry_calibrator import calibrate_industry
        return calibrate_industry(self.llm, resume_text, mode)

    # ── Feature 8A: AI Tone Detector (no LLM) ────────────────────

    @staticmethod
    def tone_detect(text: str) -> dict:
        from src.career.detectors import detect_ai_tone
        return detect_ai_tone(text)

    # ── Feature 8B: Bias & Redundancy Detector (no LLM) ──────────

    @staticmethod
    def bias_detect(text: str) -> dict:
        from src.career.detectors import detect_bias_redundancy
        return detect_bias_redundancy(text)

    # ── Feature 10: JD Manager ────────────────────────────────────

    @staticmethod
    def add_jd_text(text: str, label: str = "") -> dict:
        from src.career.jd_manager import add_jd_from_text
        return add_jd_from_text(text, label)

    @staticmethod
    def add_jd_url(url: str) -> dict:
        from src.career.jd_manager import add_jd_from_url
        return add_jd_from_url(url)

    @staticmethod
    def list_jds() -> list[dict]:
        from src.career.jd_manager import list_jds
        return list_jds()

    @staticmethod
    def get_jd_by_index(index: int):
        from src.career.jd_manager import get_jd_by_index
        return get_jd_by_index(index)

    # ── Feature 11: Resume Parser ─────────────────────────────────

    def parse_resume(self, raw_text: str, label: str = "") -> dict:
        from src.career.resume_parser import parse_resume
        return parse_resume(self.llm, raw_text, label)

    @staticmethod
    def list_parsed_resumes() -> list[dict]:
        from src.career.resume_parser import list_parsed_resumes
        return list_parsed_resumes()

    @staticmethod
    def get_parsed_resume(resume_id: int):
        from src.career.resume_parser import get_parsed_resume
        return get_parsed_resume(resume_id)

    # ── Feature 12: Smart Selector ────────────────────────────────

    def select_and_generate_latex(self, resume_parsed: dict,
                                  jd_text: str,
                                  extra_projects: list[dict] | None = None) -> dict:
        from src.career.smart_selector import select_and_rank
        return select_and_rank(self.llm, resume_parsed, jd_text, extra_projects)
