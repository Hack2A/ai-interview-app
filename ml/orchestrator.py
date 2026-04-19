"""intrv.ai ML Orchestrator — unified API for backend integration.

This is the SINGLE ENTRY POINT for the backend to access all ML functionalities.
Import this module and use the IntrvAIOrchestrator class.

Usage:
    from orchestrator import IntrvAIOrchestrator

    api = IntrvAIOrchestrator()
    api.load_documents()

    # ATS Analysis
    result = api.analyze_resume()

    # Interview (with mode and type)
    api.new_session(difficulty="Medium", interview_mode="curated", interview_type="behavioral")
    api.start_interview(difficulty="Medium", enable_proctoring=True)

    # Transcription
    text = api.transcribe_audio("path/to/audio.wav")

    # TTS
    api.speak("Hello, welcome to the interview.")

    # Evaluation
    report = api.generate_report()
"""
import json
import logging
import os
from pathlib import Path
from typing import Generator

from config import settings

logger = logging.getLogger("IntrvAI")


class IntrvAIOrchestrator:
    """Unified API for all intrv.ai ML functionalities.

    Exposes clean methods for:
    - Document loading (resume, JD)
    - ATS resume analysis (algorithmic + LLM)
    - Interview management (LLM chat, streaming)
    - Speech-to-Text (Whisper transcription)
    - Text-to-Speech (edge-tts + piper)
    - RAG (retrieval-augmented generation)
    - Proctoring (webcam monitoring)
    - Evaluation (post-interview reports)
    - Sentiment analysis
    - Cache management
    """

    def __init__(self, lazy_load: bool = True) -> None:
        """Initialize orchestrator.

        Args:
            lazy_load: If True, engines are loaded on first use (faster startup).
                       If False, all engines load immediately.
        """
        self._interview_mode: str = "generic"
        self._interview_type: str = "technical"
        self._resume_text: str | None = None
        self._jd_text: str | None = None

        # Lazy-loaded engine refs
        self._llm_engine = None
        self._stt_engine = None
        self._tts_engine = None
        self._rag_engine = None
        self._ats_checker = None
        self._evaluator = None
        self._proctoring = None
        self._sentiment = None
        self._session = None

        if not lazy_load:
            self.load_documents()
            _ = self.llm
            _ = self.stt
            _ = self.tts

        logger.info("intrv.ai Orchestrator initialized")

    # ── Document Loading ──────────────────────────────────────────

    def load_documents(self) -> dict:
        """Load resume and job description from data directories.

        Returns:
            dict with 'resume' and 'jd' keys (text or None).
        """
        from src.core.resume_loader import ResumeLoader
        from src.core.jd_loader import JDLoader

        self._resume_text = ResumeLoader().load_resume()
        jd_loader = JDLoader()
        self._jd_text = jd_loader.load_jd()

        # Index JD in RAG if available
        if self._jd_text:
            self.rag.index_jd(self._jd_text)

        return {
            "resume": self._resume_text,
            "jd": self._jd_text,
            "resume_loaded": self._resume_text is not None,
            "jd_loaded": self._jd_text is not None,
        }

    def load_resume_from_text(self, text: str) -> None:
        """Load resume from raw text (e.g., from API upload)."""
        self._resume_text = text

    def load_jd_from_text(self, text: str) -> None:
        """Load job description from raw text and index in RAG."""
        self._jd_text = text
        if text:
            self.rag.index_jd(text)

    def load_jd_from_file(self, file_path: str) -> dict:
        """Load job description from a file path (PDF or TXT).

        Args:
            file_path: Path to a .pdf or .txt JD file.

        Returns:
            dict with 'jd' text and 'jd_loaded' bool.
        """
        from src.core.jd_loader import JDLoader
        loader = JDLoader()
        jd_text = loader.load_from_path(file_path)
        if jd_text:
            self._jd_text = jd_text
            self.rag.index_jd(jd_text)
        return {"jd": self._jd_text, "jd_loaded": self._jd_text is not None}

    @property
    def resume_text(self) -> str | None:
        return self._resume_text

    @property
    def jd_text(self) -> str | None:
        return self._jd_text

    # ── Lazy Properties (engines loaded on first access) ──────────

    @property
    def llm(self):
        """LLM engine for chat/interview."""
        if self._llm_engine is None:
            from src.brain.llm_engine import LLMEngine
            self._llm_engine = LLMEngine(
                resume_text=self._resume_text,
                rag_engine=self._rag_engine,
                interview_type=self._interview_type,
            )
        return self._llm_engine

    @property
    def stt(self):
        """Speech-to-Text engine (Whisper)."""
        if self._stt_engine is None:
            from src.ears.stt_engine import STTEngine
            self._stt_engine = STTEngine()
        return self._stt_engine

    @property
    def tts(self):
        """Text-to-Speech engine (edge-tts + piper)."""
        if self._tts_engine is None:
            from src.voice.tts_engine import TTSEngine
            self._tts_engine = TTSEngine()
        return self._tts_engine

    @property
    def rag(self):
        """RAG engine for JD context retrieval."""
        if self._rag_engine is None:
            from src.brain.rag_engine import RAGEngine
            self._rag_engine = RAGEngine()
        return self._rag_engine

    @property
    def ats(self):
        """ATS resume checker."""
        if self._ats_checker is None:
            from src.core.ats_checker import ATSChecker
            llm_model = self.llm.llm if self._llm_engine else None
            self._ats_checker = ATSChecker(llm_model=llm_model)
        return self._ats_checker

    @property
    def evaluator(self):
        """Post-interview evaluator."""
        if self._evaluator is None:
            from src.brain.evaluator import Evaluator
            llm_model = self.llm.llm if self._llm_engine else None
            self._evaluator = Evaluator(
                model_path=settings.LLM_MODEL_PATH, 
                llm_model=llm_model
            )
        return self._evaluator

    @property
    def proctoring(self):
        """Webcam proctoring monitor."""
        if self._proctoring is None:
            from src.eyes.proctoring_monitor import ProctoringMonitor
            self._proctoring = ProctoringMonitor()
        return self._proctoring

    @property
    def sentiment(self):
        """Sentiment & emotion analyzer."""
        if self._sentiment is None:
            from src.ears.sentiment_analyzer import SentimentAnalyzer
            self._sentiment = SentimentAnalyzer()
        return self._sentiment

    @property
    def session(self):
        """Current interview session state."""
        if self._session is None:
            from src.core.session_state import SessionState
            self._session = SessionState()
        return self._session

    # ── ATS Analysis ──────────────────────────────────────────────

    def analyze_resume(self, resume_text: str | None = None,
                       jd_text: str | None = None) -> dict:
        """Run full ATS analysis (algorithmic + LLM + spelling + formatting).

        Args:
            resume_text: Override resume text (uses loaded if None).
            jd_text: Override JD text (uses loaded if None).

        Returns:
            dict with algorithmic_score, llm_score, combined_score, etc.
        """
        resume = resume_text or self._resume_text
        jd = jd_text or self._jd_text

        if not resume or not jd:
            return {"error": "Both resume and JD required for ATS analysis"}

        return self.ats.analyze(resume, jd)

    # ── LLM Chat ──────────────────────────────────────────────────

    def chat(self, user_input: str,
             difficulty: str = "Medium",
             question_context: dict | None = None) -> str:
        """Send a message to the LLM and get a full response (non-streaming).

        Args:
            user_input: User's message text.
            difficulty: Interview difficulty level.

        Returns:
            Full LLM response as string.
        """
        chunks = list(self.llm.generate_stream(user_input, difficulty, question_context=question_context))
        return " ".join(chunks).strip()

    def chat_stream(self, user_input: str,
                    difficulty: str = "Medium",
                    question_context: dict | None = None) -> Generator[str, None, None]:
        """Stream LLM response token-by-token.

        Args:
            user_input: User's message text.
            difficulty: Interview difficulty level.

        Yields:
            Sentence fragments as they are generated.
        """
        yield from self.llm.generate_stream(user_input, difficulty, question_context=question_context)

    def get_opening_question(self, difficulty: str = "Medium") -> str:
        """Generate the first interview question based on resume/JD context.

        Returns:
            Opening question text.
        """
        prompt = self.llm.prompt_manager.get_opening_prompt(difficulty)
        return self.chat(prompt, difficulty)

    def get_chat_history(self) -> list[dict]:
        """Return current conversation history."""
        return self.llm.get_history()

    def reset_chat(self) -> None:
        """Clear conversation history and create a new session."""
        if self._llm_engine:
            self._llm_engine.history = []
            self._llm_engine._is_first_call = True
        self._session = None

    # ── Speech-to-Text ────────────────────────────────────────────

    def transcribe_audio(self, audio_path: str,
                         language: str | None = None) -> dict:
        """Transcribe an audio file to text.

        Args:
            audio_path: Path to audio file (wav, mp3, flac, m4a, ogg).
            language: Force language (None = auto-detect).

        Returns:
            dict with 'text' and 'language' keys.
        """
        text, lang = self.stt.transcribe(audio_path, language)
        return {"text": text, "language": lang}

    # ── Text-to-Speech ────────────────────────────────────────────

    def speak(self, text: str) -> None:
        """Synthesize and play text as speech."""
        self.tts.speak_text(text)

    def synthesize_audio(self, text: str) -> str | None:
        """Synthesize text to an audio file (returns file path, no playback).

        Args:
            text: Text to synthesize.

        Returns:
            Path to generated audio file, or None on failure.
        """
        audio_path = self.tts._synthesize_edge(text)
        if not audio_path:
            audio_path = self.tts._synthesize_piper(text)
        return audio_path

    # ── RAG ───────────────────────────────────────────────────────

    def query_jd(self, query: str, top_k: int = 5) -> list[str]:
        """Query the JD index for relevant context.

        Args:
            query: Search query text.
            top_k: Number of results to return.

        Returns:
            List of relevant JD text chunks.
        """
        return self.rag.query_jd(query, top_k=top_k)

    def index_jd(self, jd_text: str) -> None:
        """Index a job description for RAG retrieval."""
        self._jd_text = jd_text
        self.rag.index_jd(jd_text)

    # ── Evaluation ────────────────────────────────────────────────

    def generate_report(self, history: list[dict] | None = None) -> dict:
        """Generate a post-interview evaluation report.

        Args:
            history: Chat history to evaluate (uses current if None).

        Returns:
            dict with score, mistakes, suggestions, domain_rating, swot_analysis.
        """
        chat_history = history or self.get_chat_history()
        return self.evaluator.generate_report(chat_history)

    # ── Proctoring ────────────────────────────────────────────────

    def start_proctoring(self) -> bool:
        """Start webcam proctoring. Returns True on success."""
        try:
            return self.proctoring.start()
        except Exception as e:
            logger.error(f"Proctoring failed to start: {e}")
            return False

    def stop_proctoring(self) -> dict:
        """Stop proctoring and return violation summary."""
        summary = self.proctoring.get_violations_summary()
        self.proctoring.stop()
        return summary

    # ── Sentiment Analysis ────────────────────────────────────────

    def analyze_sentiment(self, audio_path: str) -> dict:
        """Analyze emotion from audio file.

        Returns:
            dict with 'emotion' and 'confidence' keys.
        """
        return self.sentiment.analyze_emotion(audio_path)

    def detect_fillers(self, text: str) -> dict:
        """Detect filler words in text.

        Returns:
            dict with 'fillers' list and 'count'.
        """
        fillers = self.sentiment.detect_fillers(text)
        return {"fillers": fillers, "count": len(fillers)}

    # ── Toxicity ──────────────────────────────────────────────────

    _PROFANITY_WORDS = frozenset([
        "fuck", "shit", "bitch", "ass", "damn", "bastard", "dick",
        "asshole", "crap", "piss", "slut", "whore", "cunt", "stfu",
        "motherfucker", "bullshit", "dumbass", "idiot", "stupid",
    ])

    def check_toxicity(self, text: str) -> dict:
        """Check text for profanity/toxicity.

        Returns:
            dict with 'is_toxic' bool and 'matched_words' list.
        """
        words = set(text.lower().split())
        matched = words & self._PROFANITY_WORDS
        return {"is_toxic": bool(matched), "matched_words": list(matched)}

    # ── Session Management ────────────────────────────────────────

    def new_session(self, difficulty: str = "Medium",
                    interview_mode: str = "generic",
                    interview_type: str = "technical") -> dict:
        """Create a new interview session.

        Args:
            difficulty: Easy, Medium, Hard, or Extreme.
            interview_mode: 'generic' or 'curated'.
            interview_type: 'technical', 'behavioral', 'hr', or 'combined'.

        Returns:
            Session metadata dict.
        """
        from src.core.session_state import SessionState
        self._interview_mode = interview_mode
        self._interview_type = interview_type
        self._session = SessionState(
            difficulty=difficulty,
            interview_mode=interview_mode,
            interview_type=interview_type,
        )
        # Reset LLM engine to pick up new interview type
        self._llm_engine = None
        return self._session.to_dict()

    def get_session_info(self) -> dict:
        """Get current session metadata."""
        return self.session.to_dict()

    # ── Cache ─────────────────────────────────────────────────────

    def clear_cache(self) -> None:
        """Clear all ML caches (embeddings, LLM results)."""
        from src.core.cache_manager import get_cache_manager
        get_cache_manager().clear_cache()

    # ── Full Interview Flow (convenience) ─────────────────────────

    def run_interactive_interview(self) -> None:
        """Run the full interactive CLI interview (existing terminal flow).

        This is a convenience method that delegates to InterviewManager.
        For backend APIs, use the individual methods above instead.
        """
        from src.core.interview_manager import InterviewManager
        InterviewManager().start_session()

    # ── Question Bank RAG ─────────────────────────────────────────

    def index_question_bank(self) -> dict:
        """Index the question bank from question_bank.json into ChromaDB.

        Returns:
            dict with 'count' of indexed questions and 'status'.
        """
        from src.brain.rag_engine import QuestionBankRAG

        qb = QuestionBankRAG()

        if not settings.QUESTION_BANK_PATH.exists():
            return {"status": "error", "message": "question_bank.json not found. Run ingest_datasets.py first."}

        with open(settings.QUESTION_BANK_PATH, 'r', encoding='utf-8') as f:
            questions = json.load(f)

        count = qb.index_questions(questions)
        return {"status": "ok", "count": count}

    def get_question_from_bank(
        self,
        skills: list[str] | None = None,
        category: str | None = None,
        difficulty: str | None = None,
        top_k: int = 5,
        exclude_ids: list[str] | None = None,
    ) -> list[dict]:
        """Retrieve interview questions from the question bank.

        Args:
            skills: List of candidate skills for filtering.
            category: Filter by category (e.g., 'dsa', 'ml').
            difficulty: Filter by difficulty ('easy', 'medium', 'hard').
            top_k: Max results.
            exclude_ids: IDs of already-asked questions.

        Returns:
            List of question dicts with answer and metadata.
        """
        from src.brain.rag_engine import QuestionBankRAG

        qb = QuestionBankRAG()
        if not qb.is_indexed:
            return []

        if skills:
            return qb.retrieve_by_skills(
                skills=skills, category=category,
                difficulty=difficulty, top_k=top_k,
                exclude_ids=exclude_ids,
            )
        else:
            query = f"{category or 'general'} interview questions"
            return qb.retrieve_questions(
                query=query, top_k=top_k,
                category=category, difficulty=difficulty,
                exclude_ids=exclude_ids,
            )

    def extract_resume_skills(self, resume_text: str | None = None) -> dict:
        """Extract structured skills from resume text.

        Args:
            resume_text: Resume text. If None, uses loaded resume.

        Returns:
            dict with skills, skill_domains, interview_domains.
        """
        from src.brain.skill_extractor import SkillExtractor

        text = resume_text or self._resume_text
        if not text:
            return {"skills": [], "skill_domains": {}, "interview_domains": []}

        if hasattr(text, 'raw_text'):
            text = text.raw_text

        return SkillExtractor().extract(text)

    def run_dataset_ingestion(self) -> dict:
        """Run the dataset ingestion pipeline.

        Downloads datasets from Kaggle (requires KAGGLE_API_TOKEN env var),
        normalizes, deduplicates, and saves to question_bank.json.

        Returns:
            dict with 'status', 'output_path', and 'question_count'.
        """
        try:
            from scripts.ingest_datasets import run_ingestion
            output_path = run_ingestion()
            return {
                "status": "ok",
                "output_path": str(output_path),
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # ── Health Check ──────────────────────────────────────────────

    def health_check(self) -> dict:
        """Check which ML components are available.

        Returns:
            dict with component availability booleans.
        """
        checks = {
            "resume_loaded": self._resume_text is not None,
            "jd_loaded": self._jd_text is not None,
            "llm_ready": self._llm_engine is not None,
            "stt_ready": self._stt_engine is not None,
            "tts_ready": self._tts_engine is not None,
            "rag_ready": self._rag_engine is not None,
            "models_dir_exists": settings.MODELS_DIR.exists(),
            "llm_model_exists": settings.LLM_MODEL_PATH.exists(),
            "tts_model_exists": settings.TTS_MODEL_PATH.exists(),
            "question_bank_exists": settings.QUESTION_BANK_PATH.exists(),
        }
        checks["all_ready"] = all(checks.values())
        return checks

