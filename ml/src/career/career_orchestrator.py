"""Career Orchestrator — central entry point for all career features.

Lazy-loads the LLM and delegates to feature-specific modules.
"""
import json
import logging

from llama_cpp import Llama

from config import settings

logger = logging.getLogger("CareerOrchestrator")


class CareerOrchestrator:
    """Orchestrates all career management features with a shared LLM."""

    def __init__(self) -> None:
        self._llm: Llama | None = None

    @property
    def llm(self) -> Llama:
        """Lazy-load the LLM model (same model as the interview engine)."""
        if self._llm is None:
            logger.info(f"Loading LLM from: {settings.LLM_MODEL_PATH}")
            self._llm = Llama(
                model_path=str(settings.LLM_MODEL_PATH),
                n_ctx=settings.CONTEXT_SIZE,
                n_threads=settings.N_THREADS,
                verbose=False,
            )
            logger.info("LLM loaded for Career features")
        return self._llm

    # ── Feature 1: Match Report ───────────────────────────────────

    def match_report(self, resume_text: str, jd_text: str) -> dict:
        from src.career.match_report import generate_match_report
        return generate_match_report(self.llm, resume_text, jd_text)

    # ── Feature 2: Cover Letter ───────────────────────────────────

    def cover_letter(self, resume_text: str, jd_text: str,
                     tone: str = "professional") -> dict:
        from src.career.cover_letter import generate_cover_letter
        return generate_cover_letter(self.llm, resume_text, jd_text, tone)

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

    # ── Feature 6C: Rank Projects ─────────────────────────────────

    def rank_projects(self, projects: list[dict], jd_text: str) -> list[dict]:
        from src.career.project_manager import rank_projects
        return rank_projects(self.llm, projects, jd_text)

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
